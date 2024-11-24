import boto3
import json
import re
import os, sys
import multiprocessing as mp
import threading as th
from datetime import datetime
from private_tools import SignalHandler, SQSHandler, Database
from private_tools import Secrets, Bucket, S3CopyProgress
from private_tools import sub_json, deconstruct_path, get_parameters
from private_tools import create_upload_map


def process_object(task, c_bucket, db_secrets_vals, upload_id, ):
    db_p_client = Database(db_secrets_vals)
    # update status for copy record
    cp_rec = {'started_ts': datetime.now().timestamp(), 'updated_at': str(datetime.now())[0:19],
              'status': 1}
    db_p_client.update('object_copies', cp_rec)
    db_p_client.where(f'id = {task["obj_id"]}')
    db_p_client.run()

    # copy object
    copy_source = {'Bucket': task["source_bucket"],
                   'Key': task["source_key"]}
    response = c_bucket.upload_part_copy(Bucket=task['bucket'],
                                         CopySource=copy_source,
                                         CopySourceRange=task['byte_range'],
                                         Key=task['target_key'],
                                         PartNumber=str(task['part']),
                                         UploadId=upload_id)
    multipart_upload_block['ETag'] = response['CopyPartResult']['ETag']
    multipart_upload_block['PartNumber'] = response['CopyPartResult']['PartNumber']
    if response['CopyPartResult']['ChecksumCRC32']:
        multipart_upload_block['ChecksumCRC32'] = response['CopyPartResult']['ChecksumCRC32']
    if response['CopyPartResult']['ChecksumCRC32C']:
        multipart_upload_block['ChecksumCRC32C'] = response['CopyPartResult']['ChecksumCRC32C']
    if response['CopyPartResult']['ChecksumSHA1']:
        multipart_upload_block['ChecksumSHA1'] = response['CopyPartResult']['ChecksumSHA1']
    if response['CopyPartResult']['ChecksumSHA256']:
        multipart_upload_block['ChecksumSHA256'] = response['CopyPartResult']['ChecksumSHA256']
    # upd_connect = Database(db_secrets_vals)
    # progress_copy = S3CopyProgress({'id': task["obj_id"], 'key': task["source_key"],
    #                                'size': obj_info['ContentLength']}, db_secrets_vals)
    # try:
    #    copy_source = {'Bucket': task["source_bucket"],
    #                   'Key': task["source_key"]}
    #    r_bucket.cp(copy_source, task['target_bucket'], task['target_obj'], progress_copy.update_progress,
    #                task['locking'])
    # except Exception as error:
    #    raise error
    # else:
    #    # update record
    #    obj_info = c_bucket.get_object_info(task["target_bucket"],
    #                                        task["target_obj"])
    #    if obj_info is not None:
    #        cp_rec = {'etag': obj_info['ETag'].replace('"', ''), 'finished_ts': datetime.now().timestamp(),
    #                  'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 0}
    #        db_p_client.update('object_copies', cp_rec)
    #        db_p_client.where(f'id = {task["obj_id"]}')
    #        db_p_client.run()
    #        c_bucket.rm_object(task['source_bucket'],
    #                           task['source_key'])
    return True


def process_backups():
    ssm_id = os.getenv('SSM_ID')
    parameters = get_parameters(ssm_id, 'eu-west-2')
    max_th = mp.cpu_count() * 4

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
    # db_client = Database(db_secrets_vals)
    queue_client = SQSHandler(parameters['queue_name'], account, parameters['aws_region'])
    s3_client = Bucket()
    default_target_bucket = 'tna-backup-vault'
    while signal_handler.can_run():
        # read sqs queue, update DB and create file copying queue for multi processing
        db_client = Database(db_secrets_vals)
        queue_response = queue_client.receive_message(10)
        if signal_handler.shutdown_requested:
            # print('shutting down')
            db_client.close()
            sys.exit(0)
        # print('reading message queue')
        if 'Messages' in queue_response:
            task_list = []
            for message in queue_response['Messages']:
                message_body = json.loads(sub_json(message['Body'], regex_set))
                checkin_id = message_body['file_id']
                # read queue entry
                db_client.select('queues', ['*'])
                db_client.where(f'message_id = "{message["MessageId"]}"')
                queue_rec = db_client.fetch()
                if not bool(queue_rec):
                    del queue_rec
                    # remove from queue
                    queue_client.delete_message(message['ReceiptHandle'])
                    continue
                else:
                    # read checkin entry
                    db_client.select('object_checkins', ['*'])
                    db_client.where(f'id = {checkin_id}')
                    checkin_rec = db_client.fetch()
                    if checkin_rec['status'] == 8:  # queue entry is redundant
                        queue_client.delete_message(message['ReceiptHandle'])
                        queue_data = {'status': 8, 'finished_ts': datetime.now().timestamp()}
                        db_client.where(f'checkin_id = {message_body["file_id"]}')
                        db_client.update('queues', queue_data)
                        db_client.run()
                    else:
                        # get object data
                        obj_info = s3_client.get_object_info(bucket=checkin_rec['bucket'],
                                                             key=checkin_rec['object_key'])
                        object_name_parts = deconstruct_path(checkin_rec['object_key'])
                        if obj_info is None:
                            queue_client.delete_message(message['ReceiptHandle'])
                        else:
                            db_client.select('ap_targets', ['access_point', 'name_processing'])
                            db_client.where(f'access_point = "{object_name_parts["access_point"]}"')
                            ap_rec = db_client.fetch()
                            if ap_rec:
                                s3_target = ap_rec['bucket']
                                name_processing = ap_rec['name_processing']
                            else:
                                s3_target = default_target_bucket
                                name_processing = 1
                            # check of any changes
                            # write to table copies
                            if name_processing == 1:
                                tn_split = checkin_rec["object_name"].split('.')
                                if len(tn_split) > 1:
                                    target_name = f'{".".join(tn_split[:-1])}_{str(datetime.now().timestamp()).replace(".", "_")}.{"".join(tn_split[-1:])}'
                                else:
                                    target_name = f'{checkin_rec["object_name"]}_{str(datetime.now().timestamp()).replace(".", "_")}'
                            else:
                                target_name = checkin_rec['object_name']
                            object_copy = {'queue_id': queue_rec['id'], 'checkin_id': checkin_rec['id'],
                                           'object_name': target_name, 'source_name': checkin_rec['object_name'],
                                           'access_point': object_name_parts["access_point"],
                                           'object_size': obj_info['content_length'],
                                           'object_type': obj_info['content_type'],
                                           'etag': obj_info['etag'].replace('"', ''),
                                           'object_key': checkin_rec['object_key'],
                                           'bucket': s3_target,
                                           'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                           'status': 2,
                                           'percentage': '0.00'}
                            locking_info = {}
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
                                object_copy['checksum_sha1'] = checkin_rec['ChecksumSHA1']
                            if 'ChecksumSHA256' in obj_info:
                                object_copy['checksum_sha256'] = checkin_rec['checksum_sha1']
                            db_client.insert('object_copies', object_copy)
                            obj_id = db_client.run()
                            # remove from queue
                            queue_client.delete_message(message['ReceiptHandle'])
                            # add mp queue
                            task_list.append({'checkin_id': checkin_rec['id'], 'obj_id': obj_id,
                                              'source_bucket': checkin_rec['bucket'],
                                              'source_key': checkin_rec['object_key'],
                                              'access_point': object_name_parts['access_point'],
                                              'target_bucket': s3_target,
                                              'target_obj': f'{object_name_parts["location"]}/{target_name}'.lstrip(
                                                  '/'), 'locking': locking_info,
                                              'content_length': obj_info['content_length']})
            if task_list:
                job_list = []
                for task in task_list:
                    upload_map = create_upload_map(task['content_length'])
                    position = 1
                    for entry in upload_map:
                        percentage = (entry[1] - entry[0]) * 100 / task['content_length']
                        byte_range = f'bytes={entry[0]}-{entry[1]}'
                        job_list.append({'checkin_id': task['checkin_id'], 'obj_id': task['obj_id'],
                                         'source_bucket': task['source_bucket'], 'source_key': task['source_key'],
                                         'access_point': task['access_point'],
                                         'target_bucket': task['target_bucket'],
                                         'target_obj': task["target_obj"], 'locking': task['locking'],
                                         'content_length': task['content_length'], 'percentage': percentage,
                                         'byte_range': byte_range, 'part': position,
                                         'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                         'status': 0})
                        position += 1
                    multipart_upload_block = {'Parts': []}
                    upload_id = s3_client.create_multipart_upload(task['target_bucket'],
                                                                  task['target_obj'])
                    for job in job_list:
                        copy_source = {'Bucket': job["source_bucket"],
                                       'Key': job["source_key"]}
                        response = s3_client.upload_part_copy(copy_source, job['target_bucket'], job['target_obj'],
                                                              job['byte_range'], upload_id, job['part'])
                        multipart_upload_block['Parts'].append(response)
                    complete_upload = s3_client.complete_multipart_upload(task['target_bucket'], task['target_obj'],
                                                                          multipart_upload_block, upload_id)

        del queue_response
        db_client.close()


if __name__ == "__main__":
    process_backups()
