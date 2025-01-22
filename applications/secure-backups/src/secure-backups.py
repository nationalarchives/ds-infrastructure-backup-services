import boto3
import json
import re
import os, sys
from datetime import datetime
from private_tools import SignalHandler, SQSHandler, Database
from private_tools import Secrets, Bucket
from private_tools import sub_json, deconstruct_path, get_parameters
from private_tools import create_upload_map, process_obj_name


def process_backups():
    ssm_id = os.getenv('SSM_ID')
    parameters = get_parameters(ssm_id, 'eu-west-2')

    signal_handler = SignalHandler()
    regex_line = re.compile(r'(?<![{}\[\]])\n')
    regex_comma = re.compile(r',(?=\s*?[{\[\]}])')
    client = boto3.client('sts')
    response = client.get_caller_identity()
    account = response['Account']
    db_secrets = Secrets(parameters['asm_id'])
    regex_set = [{'re_compile': regex_line, 'replace_with': ',\n'},
                 {'re_compile': regex_comma, 'replace_with': ''}]
    db_secrets_vals = json.loads(db_secrets.get_secrets())
    queue_client = SQSHandler(parameters['queue_name'], account, parameters['aws_region'])
    s3_client = Bucket()
    default_target_bucket = 'tna-backup-vault'
    default_source_account_id = account
    while signal_handler.can_run():
        # read sqs queue, update DB and create file copying queue for multi processing
        if signal_handler.shutdown_requested:
            sys.exit(0)
        queue_response = queue_client.receive_message(1)
        print('receive_message')
        print(queue_response)
        if 'Messages' in queue_response:
            print('Message ingest')
            task_list = []
            db_client = Database(db_secrets_vals)
            for message in queue_response['Messages']:
                print('message processing')
                message_body = json.loads(sub_json(message['Body'], regex_set))
                checkin_id = message_body['checkin_id']
                # read queue entry
                db_client.select('queues', ['id', 'message_id', 'status'])
                db_client.where(f'message_id = "{message["MessageId"]}"')
                queue_rec = db_client.fetch()
                queue_client.delete_message(message['ReceiptHandle'])
                if queue_rec is None:
                    print('message id not found in db')
                    del queue_rec
                    # remove from queue
                    continue
                elif queue_rec['status'] > 0:
                    print('message status is greater than 0')
                    del queue_rec
                    # remove from queue
                    continue
                else:
                    print('message start')
                    # update queue record
                    db_client.where(f'checkin_id = {checkin_id}')
                    db_client.update('queues', {'status': 1,
                                                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                    db_client.run()
                    # read checkin entry
                    db_client.select('object_checkins', ['*'])
                    db_client.where(f'id = {checkin_id}')
                    checkin_rec = db_client.fetch()
                    if checkin_rec is None:
                        print('intake checkin not found')
                        db_client.where(f'id = {queue_rec["id"]}')
                        db_client.update('queues', {'status': 8, 'finished_ts': datetime.now().timestamp(),
                                                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                        db_client.run()
                        continue
                    elif checkin_rec['status'] > 1:
                        print('intake status is greater than 1')
                        db_client.where(f'id = {queue_rec["id"]}')
                        db_client.update('queues', {'status': 5, 'finished_ts': datetime.now().timestamp(),
                                                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                        db_client.run()
                        continue
                    else:
                        # get object data
                        print(f"1- {checkin_rec['bucket']} {checkin_rec['object_key']}")
                        obj_info = s3_client.get_object_info(bucket=checkin_rec['bucket'],
                                                             key=checkin_rec['object_key'])
                        print(f"2 - {obj_info}")
                        if obj_info is None:
                            db_client.where(f'checkin_id = {checkin_id}')
                            db_client.update('queues', {'status': 8,
                                                        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                            db_client.run()
                            db_client.where(f'id = {checkin_id}')
                            db_client.update('object_checkins', {'status': 9,
                                                                 'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                            db_client.run()
                            continue
                        else:
                            db_client.where(f'id = {checkin_id}')
                            db_client.update('object_checkins', {'status': 2,
                                                                 'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                            db_client.run()
                            ap_rec_fields = ['access_point', 'access_point_entry', 'target_bucket', 'target_location',
                                             'storage_class', 'expiration_period', 'retention_period', 'legal_hold',
                                             'lock_mode', 'name_processing', 'source_account_id', 'compress']
                            db_client.select('target_endpoints', ap_rec_fields)
                            # create location query
                            object_key_parts = deconstruct_path(checkin_rec['object_key'])
                            print(f"3 - {object_key_parts}")
                            if len(object_key_parts["location_filters"]) > 0:
                                lfilter = ""
                                for filter in object_key_parts["location_filters"]:
                                    lfilter = lfilter + f'access_point_entry = "{filter}" OR '
                                lfilter = lfilter[0:-4]
                                print(f"4 - {lfilter}")
                                db_client.where(f'{lfilter}')
                                db_client.order_by('length(access_point) DESC')
                            else:
                                db_client.where(f'access_point IS NULL')
                            ap_rec = db_client.fetch()
                            if ap_rec:
                                access_point = ap_rec['access_point']
                                access_point_entry = ap_rec['access_point_entry']
                                target_bucket = ap_rec['target_bucket']
                                name_processing = ap_rec['name_processing']
                                source_account_id = ap_rec['source_account_id']
                                target_destination = f"{checkin_rec['object_key'][len(ap_rec['access_point_entry']) + 1:]}"
                                target_key = f"{target_destination}/{object_key_parts['object_name']}"
                            else:
                                access_point = "none"
                                access_point_entry = "none"
                                target_bucket = default_target_bucket
                                name_processing = 1
                                source_account_id = default_source_account_id
                                target_destination = object_key_parts['location']
                                target_key = f"{target_destination}/{object_key_parts['object_name']}"
                            print(f"5 - {target_bucket} - {target_destination}")
                            print(f"6 - {target_key}")
                            # check of any changes
                            # write to table copies
                            target_name = process_obj_name(checkin_rec["object_name"], name_processing)
                            obj_cp_rec = {'queue_id': queue_rec['id'], 'checkin_id': checkin_rec['id'],
                                          'source_name': checkin_rec['object_name'],
                                          'source_account_id': source_account_id,
                                          'access_point': access_point,
                                          'target_bucket': target_bucket,
                                          'target_name': target_name,
                                          'target_key': target_key,
                                          'target_size': obj_info['content_length'],
                                          'target_type': obj_info['content_type'],
                                          'etag': obj_info['etag'].replace('"', ''),
                                          'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                          'status': 0, 'percentage': '0.00', 'received_ts': datetime.now().timestamp()}
                            if 'retain_until_date' in obj_info:
                                obj_cp_rec['retain_until_date'] = checkin_rec['retain_until_date']
                            if 'lock_mode' in obj_info:
                                obj_cp_rec['lock_mode'] = checkin_rec['lock_mode']
                            if 'legal_hold' in obj_info:
                                obj_cp_rec['legal_hold'] = checkin_rec['legal_hold']
                            if 'checksum_crc32' in obj_info:
                                obj_cp_rec['checksum_crc32'] = checkin_rec['checksum_crc32']
                            if 'checksum_crc32c' in obj_info:
                                obj_cp_rec['checksum_crc32c'] = checkin_rec['checksum_crc32c']
                            if 'checksum_sha1' in obj_info:
                                obj_cp_rec['checksum_sha1'] = checkin_rec['checksum_sha1']
                            if 'sse_customer_algorithm' in obj_info:
                                obj_cp_rec['sse_customer_algorithm'] = checkin_rec['sse_customer_algorithm']
                            if 'checksum_sha256' in obj_info:
                                obj_cp_rec['checksum_sha256'] = checkin_rec['checksum_sha256']
                            if 'checksum_sha256' in obj_info:
                                obj_cp_rec['checksum_sha256'] = checkin_rec['checksum_sha256']
                            if 'checksum_sha256' in obj_info:
                                obj_cp_rec['checksum_sha256'] = checkin_rec['checksum_sha256']
                            db_client.insert('object_copies', obj_cp_rec)
                            copy_id = db_client.run()
                            # update checkin record
                            db_client.where(f'id = {checkin_rec["id"]}')
                            db_client.update('object_checkins', {'copy_id': copy_id, 'status': 3,
                                                                 'finished_ts': datetime.now().timestamp()})
                            # add mp queue
                            task_list.append({'checkin_id': checkin_rec['id'], 'copy_id': copy_id,
                                              'source_bucket': checkin_rec['bucket'],
                                              'source_key': checkin_rec['object_key'],
                                              'access_point': access_point,
                                              'target_bucket': target_bucket,
                                              'target_key': target_key,
                                              'content_length': obj_info['content_length'],
                                              'source_account_id': source_account_id})
                    del checkin_rec
                    # update queue record
                    db_client.where(f'checkin_id = {checkin_id}')
                    db_client.update('queues', {'status': 2,
                                                'finished_ts': datetime.now().timestamp()})
                    db_client.run()
            print(f"7 - {task_list}")
            if task_list:
                for task in task_list:
                    upload_map = create_upload_map(task['content_length'])
                    position = 1
                    job_list = []
                    for entry in upload_map:
                        percentage = str(round((entry[2] * 100 / task['content_length']), 2))
                        byte_range = f'bytes={entry[0]}-{entry[1]}'
                        part_upload_data = {'checkin_id': task['checkin_id'], 'copy_id': task['copy_id'],
                                            'source_bucket': task['source_bucket'], 'source_key': task['source_key'],
                                            'access_point': task['access_point'],
                                            'target_bucket': task['target_bucket'],
                                            'target_key': task["target_key"],
                                            'content_length': entry[2], 'percentage': percentage,
                                            'byte_range': byte_range, 'part': position,
                                            'source_account_id': task["source_account_id"],
                                            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            'status': 0}
                        db_client.insert('part_uploads', part_upload_data)
                        part_upload_id = db_client.run()
                        part_upload_data['part_upload_id'] = part_upload_id
                        job_list.append(part_upload_data)
                        position += 1
                    multipart_upload_block = {'Parts': []}
                    upload_id = s3_client.create_multipart_upload(task['target_bucket'],
                                                                  task['target_key'])
                    for job in job_list:
                        print(
                            f'sb: {job["source_bucket"]} | so: {job["source_key"]} tb: {job["target_bucket"]} | to: {job["target_key"]} | bytes: {job["byte_range"]} | part: {job["part"]}')
                        copy_source = {'Bucket': job["source_bucket"],
                                       'Key': job["source_key"]}
                        response = s3_client.upload_part_copy(copy_src=copy_source, endpoint=job['target_bucket'],
                                                              target_key=job['target_key'],
                                                              copy_source_range=job['byte_range'], upload_id=upload_id,
                                                              part_number=job['part'])
                        multipart_upload_block['Parts'].append(response)
                        job_data = {'status': 2, 'finished_ts': datetime.now().timestamp()}
                        db_client.where(f'id = {job["part_upload_id"]}')
                        db_client.update('part_uploads', job_data)
                        copy_data = {'percentage': f'@percentage + {job["percentage"]}'}
                        db_client.where(f'id = {job["copy_id"]}')
                        db_client.update('object_copies', copy_data)
                        db_client.run()
                    complete_upload = s3_client.complete_multipart_upload(task['target_bucket'], task['target_key'],
                                                                          multipart_upload_block, upload_id)
                    copy_data = {'percentage': '100.00', 'finished_ts': datetime.now().timestamp(),
                                 'etag': complete_upload['etag'].replace('"', ''),
                                 'upload_id': upload_id, 'status': 3, }
                    if 'VersionId' in complete_upload:
                        copy_data['version_id'] = complete_upload['VersionId']
                    if 'ServerSideEncryption' in complete_upload:
                        copy_data['server_side_encryption'] = complete_upload['ServerSideEncryption']
                    if 'SSEKMSKeyId' in complete_upload:
                        copy_data['sse_kms_key_id'] = complete_upload['SSEKMSKeyId']
                    if 'Expiration' in complete_upload:
                        copy_data['expiration'] = complete_upload['Expiration']
                    if 'ChecksumCRC32' in complete_upload:
                        copy_data['checksum_crc32'] = complete_upload['ChecksumCRC32']
                    if 'ChecksumCRC32C' in complete_upload:
                        copy_data['checksum_crc32c'] = complete_upload['ChecksumCRC32C']
                    if 'ChecksumSHA1' in complete_upload:
                        copy_data['checksum_sha1'] = complete_upload['ChecksumSHA1']
                    if 'ChecksumSHA256' in complete_upload:
                        copy_data['checksum_sha256'] = complete_upload['ChecksumSHA256']
                    db_client.where(f'id = {task["copy_id"]}')
                    db_client.update('object_copies', copy_data)
                    db_client.run()
                    s3_client.rm_object(task['source_bucket'], task['source_key'])
                    del job_list
            db_client.close()
        del queue_response


if __name__ == "__main__":
    process_backups()
