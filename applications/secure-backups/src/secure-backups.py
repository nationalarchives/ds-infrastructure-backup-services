import boto3
import botocore.exceptions
import json
import re
import os
import multiprocessing as mp
from multiprocessing import Process, Queue
from datetime import datetime
from private_tools import SignalHandler, SQSHandler, Database
from private_tools import Secrets, Bucket, sub_json, find_key_dict, deconstruct_path
from private_tools import get_parameters


def process_object(tasks, done, bucket, db):
    object_queue_data = tasks.get()
    print(object_queue_data)
    # update record
    cp_rec = {'started_ts': datetime.now().timestamp(), 'updated_at': str(datetime.now())[0:19],
              'status': 1}
    db.update('object_copies', cp_rec)
    db.where(f'id = {object_queue_data["obj_id"]}')
    db.run()
    # copy object
    try:
        response = bucket.copy_object(Bucket=object_queue_data['target_bucket'],
                                      Key=object_queue_data['target_obj'],
                                      CopySource=f'{object_queue_data["source_bucket"]}/{object_queue_data["source_key"]}')
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'ObjectNotInActiveTierError':
            print('S3 - ObjectNotInActiveTierError')
        else:
            print('S3 - unknown error')
        raise error
    else:
        # update record
        cp_rec = {'etag': response['CopyObjectResult']['ETag'].replace('"', ''), 'finished_ts': datetime.now().timestamp(),
                  'updated_at': str(datetime.now())[0:19], 'status': 0}
        db.update('object_copies', cp_rec)
        db.where(f'id = {object_queue_data["obj_id"]}')
        db.run()
        bucket.delete_object(Bucket=object_queue_data["source_bucket"],
                             Key=object_queue_data["source_key"],
                             BypassGovernanceRetention=True)
        action = tasks.get()
        done.put(action)

def process_backups():
    ssm_id = os.getenv('SSM_ID')
    parameters = get_parameters(ssm_id, 'eu-west-2')
    max_pp = mp.cpu_count()

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
    db_client = Database(db_secrets_vals)
    queue_client = SQSHandler(parameters['queue_name'], account, parameters['aws_region'])
    bucket_client = Bucket()
    s3_source = 'tna-backup-drop-zone'
    s3_target = 'tna-backup-vault'

    while signal_handler.can_run():
        # read sqs queue, update DB and create file copying queue for multi processing
        queue_response = queue_client.receive_message()
        if 'Messages' in queue_response:
            task_queue = Queue()
            done_queue = Queue()
            for message in queue_response['Messages']:
                queue_message_body = json.loads(sub_json(message['Body'], regex_set))
                checkin_file_id = queue_message_body['file_id']
                checkin_bucket = queue_message_body['bucket']
                # read queue entry
                db_client.select('queues', ['*'])
                db_client.where(f'message_id = "{message["MessageId"]}"')
                queue_rec = db_client.fetch()
                # read checkin entry
                db_client.select('object_checkins', ['*'])
                db_client.where(f'id = {checkin_file_id}')
                checkin_rec = db_client.fetch()
                if checkin_rec['status'] == 8: # queue entry is redundant
                    queue_client.delete_message(message['ReceiptHandle'])
                    queue_data = {'status': 8, 'finished_ts': datetime.now().timestamp()}
                    db_client.where(f'file_id = {queue_message_body["file_id"]}')
                    db_client.update('queues', queue_data)
                else:
                    # get object data
                    obj_info = bucket_client.get_object_info(checkin_rec['bucket'], checkin_rec['object_key'])
                    obj_attr = bucket_client.get_object_attr(checkin_rec['bucket'], checkin_rec['object_key'])
                    # check of any changes
                    # write to table copies
                    object_copy = {'queue_id': queue_rec['id'], 'checkin_id': checkin_rec['id'],
                                   'object_name': checkin_rec['object_name'], 'target_name': checkin_rec['target_name'],
                                   'object_size': obj_info['ContentLength'], 'object_type': obj_info['ContentType'],
                                   'etag': obj_info['ETag'].replace('"', ''), 'object_key': checkin_rec['object_key'],
                                   'target_bucket': s3_target, 'created_at': str(datetime.now())[0:19], 'status': 2,
                                   'percentage': '0.00'}
                    if "Metadata" in obj_info:
                        obj_metadata = obj_info['Metadata']
                        if find_key_dict("retention_period", obj_metadata):
                            object_copy['retention_period'] = obj_metadata['retention_period']
                        if find_key_dict("lock_mode", obj_metadata):
                            object_copy['lock_mode'] = obj_metadata['lock_mode']
                        if find_key_dict("legal_hold", obj_metadata):
                            object_copy['legal_hold'] = obj_metadata['legal_hold']
                        if find_key_dict("lock-until-date", obj_metadata):
                            object_copy['lock_until_date'] = obj_metadata['lock-until-date']
                    if 'Checksum' in obj_attr:
                        object_checksum = obj_attr['Checksum']
                        if 'ChecksumCRC32' in object_checksum:
                            object_copy['checksum_crc32'] = object_checksum['ChecksumCRC32']
                        if 'ChecksumCRC32C' in object_checksum:
                            object_copy['checksum_crc32c'] = object_checksum['ChecksumCRC32C']
                        if 'ChecksumSHA1' in object_checksum:
                            object_copy['checksum_sha1'] = object_checksum['ChecksumSHA1']
                        if 'ChecksumSHA256' in object_checksum:
                            object_copy['checksum_sha256'] = object_checksum['ChecksumSHA256']
                    db_client.insert('object_copies', object_copy)
                    obj_id = db_client.run()
                    # remove from queue
                    queue_client.delete_message(message['ReceiptHandle'])
                    # add mp queue
                    object_name_parts = deconstruct_path(checkin_rec['object_key'])
                    task_queue.put({'obj_id': obj_id,
                                    'source_bucket': checkin_rec['bucket'],
                                    'source_key': checkin_rec['object_key'],
                                    'target_bucket': s3_target,
                                    'target_obj': f'{object_name_parts["location"]}/{checkin_rec["target_name"]}'.lstrip('/')})
                    # run copying processes
                    for i in range(max_pp):
                        Process(target=process_object, args=(task_queue, done_queue, bucket_client, db_client,)).start()

                    for i in range(max_pp):
                        task_queue.put('STOP')
    db_client.close()


if __name__ == "__main__":
    process_backups()
