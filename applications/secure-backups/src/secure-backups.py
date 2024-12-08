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
        queue_response = queue_client.receive_message(10)
        if signal_handler.shutdown_requested:
            sys.exit(0)
        if 'Messages' in queue_response:
            task_list = []
            db_client = Database(db_secrets_vals)
            for message in queue_response['Messages']:
                message_body = json.loads(sub_json(message['Body'], regex_set))
                checkin_id = message_body['checkin_id']
                # read queue entry
                db_client.select('queues', ['*'])
                db_client.where(f'message_id = "{message["MessageId"]}"')
                queue_rec = db_client.fetch()
                if queue_rec is None:
                    del queue_rec
                    # remove from queue
                    queue_client.delete_message(message['ReceiptHandle'])
                    continue
                else:
                    # read checkin entry
                    checkin_fl = ['id', 'bucket', 'object_key', 'object_name', 'retain_until_date', 'lock_mode',
                                  'legal_hold', 'checksum_crc32', 'checksum_crc32c', 'checksum_sha1',
                                  'checksum_sha256', 'status']
                    db_client.select('object_checkins', checkin_fl)
                    db_client.where(f'id = {checkin_id}')
                    checkin_rec = db_client.fetch()
                    if checkin_rec['status'] == 5:  # queue entry is redundant - ignore
                        queue_client.delete_message(message['ReceiptHandle'])
                        queue_data = {'status': 5, 'finished_ts': datetime.now().timestamp()}
                        db_client.where(f'checkin_id = {checkin_id}')
                        db_client.update('queues', queue_data)
                        db_client.run()
                    else:
                        # get object data
                        obj_info = s3_client.get_object_info(bucket=checkin_rec['bucket'],
                                                             key=checkin_rec['object_key'])
                        if obj_info is None:
                            queue_client.delete_message(message['ReceiptHandle'])
                            queue_data = {'status': 9, 'finished_ts': datetime.now().timestamp()}
                            db_client.where(f'checkin_id = {checkin_id}')
                            db_client.update('queues', queue_data)
                            db_client.run()
                        else:
                            object_name_parts = deconstruct_path(checkin_rec['object_key'])
                            db_client.select('ap_targets', ['access_point', 'name_processing', 'kms_key_arn'])
                            db_client.where(f'access_point = "{object_name_parts["access_point"]}"')
                            ap_rec = db_client.fetch()
                            if ap_rec:
                                s3_target = ap_rec['bucket']
                                name_processing = ap_rec['name_processing']
                                kms_key_arn = ap_rec['kms_key_arn']
                                source_account_id = ap_rec['source_account_id']
                            else:
                                s3_target = default_target_bucket
                                name_processing = 1
                                kms_key_arn = None
                                source_account_id = default_source_account_id
                            # check of any changes
                            # write to table copies
                            target_name = process_obj_name(checkin_rec["object_name"], name_processing)
                            object_copy = {'queue_id': queue_rec['id'], 'checkin_id': checkin_rec['id'],
                                           'object_name': target_name, 'source_name': checkin_rec['object_name'],
                                           'access_point': object_name_parts["access_point"],
                                           'object_size': obj_info['content_length'],
                                           'object_type': obj_info['content_type'],
                                           'source_account_id': source_account_id,
                                           'etag': obj_info['etag'].replace('"', ''),
                                           'object_key': checkin_rec['object_key'], 'bucket': s3_target,
                                           'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                           'status': 0, 'percentage': '0.00', 'received_ts': datetime.now().timestamp()}
                            if kms_key_arn:
                                object_copy['kms_key_arn'] = kms_key_arn
                            if 'retain_until_date' in obj_info:
                                object_copy['retain_until_date'] = checkin_rec['retain_until_date']
                            if 'lock_mode' in obj_info:
                                object_copy['lock_mode'] = checkin_rec['lock_mode']
                            if 'legal_hold' in obj_info:
                                object_copy['legal_hold'] = checkin_rec['legal_hold']
                            if 'checksum_crc32' in obj_info:
                                object_copy['checksum_crc32'] = checkin_rec['checksum_crc32']
                            if 'checksum_crc32c' in obj_info:
                                object_copy['checksum_crc32c'] = checkin_rec['checksum_crc32c']
                            if 'checksum_sha1' in obj_info:
                                object_copy['checksum_sha1'] = checkin_rec['checksum_sha1']
                            if 'sse_customer_algorithm' in obj_info:
                                object_copy['sse_customer_algorithm'] = checkin_rec['sse_customer_algorithm']
                            if 'checksum_sha256' in obj_info:
                                object_copy['checksum_sha256'] = checkin_rec['checksum_sha256']
                            if 'checksum_sha256' in obj_info:
                                object_copy['checksum_sha256'] = checkin_rec['checksum_sha256']
                            if 'checksum_sha256' in obj_info:
                                object_copy['checksum_sha256'] = checkin_rec['checksum_sha256']
                            db_client.insert('object_copies', object_copy)
                            copy_id = db_client.run()
                            # update checkin record
                            checkin_upd = {'copy_id': copy_id, 'status': 2, 'finished_ts': datetime.now().timestamp()}
                            db_client.where(f'id = {checkin_rec["id"]}')
                            db_client.update('checkins', checkin_upd)
                            # update queue record
                            queue_data = {'status': 0, 'finished_ts': datetime.now().timestamp()}
                            db_client.where(f'checkin_id = {checkin_id}')
                            db_client.update('queues', queue_data)
                            db_client.run()
                            # remove from queue
                            queue_client.delete_message(message['ReceiptHandle'])
                            # add mp queue
                            task_list.append({'checkin_id': checkin_rec['id'], 'copy_id': copy_id,
                                              'source_bucket': checkin_rec['bucket'],
                                              'source_key': checkin_rec['object_key'],
                                              'access_point': object_name_parts['access_point'],
                                              'target_bucket': s3_target,
                                              'target_key': f'{object_name_parts["location"]}/{target_name}'.lstrip('/'),
                                              'content_length': obj_info['content_length'],
                                              'source_account_id': source_account_id, 'kms_key_arn': kms_key_arn})
                    del checkin_rec
            if task_list:
                job_list = []
                for task in task_list:
                    upload_map = create_upload_map(task['content_length'])
                    position = 1
                    for entry in upload_map:
                        percentage = str(round(((entry[1] - entry[0]) * 100 / task['content_length']), 2))
                        byte_range = f'bytes={entry[0]}-{entry[1]}'
                        part_upload_data = {'checkin_id': task['checkin_id'], 'copy_id': task['copy_id'],
                                            'source_bucket': task['source_bucket'], 'source_key': task['source_key'],
                                            'access_point': task['access_point'],
                                            'target_bucket': task['target_bucket'],
                                            'target_key': task["target_key"],
                                            'content_length': task['content_length'], 'percentage': percentage,
                                            'byte_range': byte_range, 'part': position,
                                            'source_account_id': task["source_account_id"],
                                            'kms_key_arn': task["kms_key_arn"],
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
                        copy_source = {'Bucket': job["source_bucket"],
                                       'Key': job["source_key"]}
                        response = s3_client.upload_part_copy(copy_source, job['target_bucket'], job['target_key'],
                                                              job['byte_range'], upload_id, job['part'])
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
                                 'upload_id': upload_id, }
                    if 'VersionId' in complete_upload:
                        object_copy['version_id'] = complete_upload['VersionId']
                    if 'ServerSideEncryption' in complete_upload:
                        object_copy['server_side_encryption'] = complete_upload['ServerSideEncryption']
                    if 'SSEKMSKeyId' in complete_upload:
                        object_copy['sse_kms_key_id'] = complete_upload['SSEKMSKeyId']
                    if 'Expiration' in complete_upload:
                        object_copy['expiration'] = complete_upload['Expiration']
                    if 'ChecksumCRC32' in complete_upload:
                        object_copy['checksum_crc32'] = complete_upload['ChecksumCRC32']
                    if 'ChecksumCRC32C' in complete_upload:
                        object_copy['checksum_crc32c'] = complete_upload['ChecksumCRC32C']
                    if 'ChecksumSHA1' in complete_upload:
                        object_copy['checksum_sha1'] = complete_upload['ChecksumSHA1']
                    if 'ChecksumSHA256' in complete_upload:
                        object_copy['checksum_sha256'] = complete_upload['ChecksumSHA256']
                    db_client.where(f'id = {task["copy_id"]}')
                    db_client.update('object_copies', copy_data)
                    db_client.run()
                    s3_client.rm_object(task['source_bucket'], task['source_key'])
            db_client.close()
        del queue_response


if __name__ == "__main__":
    process_backups()
