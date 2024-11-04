import boto3
import json
import re
import os, sys
import multiprocessing as mp
import queue
from datetime import datetime
from private_tools import SignalHandler, SQSHandler, Database
from private_tools import Secrets, Bucket, RBucket, S3CopyProgress
from private_tools import sub_json, find_key_dict, deconstruct_path, get_parameters


def process_object(tasks, db_secrets_vals, r_bucket, c_bucket):
    db_p_client = Database(db_secrets_vals)
    while True:
        try:
            task = tasks.get_nowait()
        except queue.Empty:
            break
        else:
            # check if source exists
            obj_info = c_bucket.get_object_info(task["source_bucket"], task["source_key"])
            if obj_info is not None:
                # update status for copy record
                cp_rec = {'started_ts': datetime.now().timestamp(), 'updated_at': str(datetime.now())[0:19],
                          'status': 1}
                db_p_client.update('object_copies', cp_rec)
                db_p_client.where(f'id = {task["obj_id"]}')
                db_p_client.run()
                # copy object
                upd_connect = Database(db_secrets_vals)
                progress_copy = S3CopyProgress({'id': task["obj_id"], 'key': task["source_key"],
                                                'size': obj_info['ContentLength']}, db_secrets_vals)
                try:
                    copy_source = {'Bucket': task["source_bucket"],
                                   'Key': task["source_key"]}
                    r_bucket.cp(copy_source, task['target_bucket'], task['target_obj'], progress_copy.update_progress, task['locking'])
                except Exception as error:
                    raise error
                else:
                    # update record
                    obj_info = c_bucket.get_object_info(task["target_bucket"],
                                                        task["target_obj"])
                    if obj_info is not None:
                        cp_rec = {'etag': obj_info['ETag'].replace('"', ''), 'finished_ts': datetime.now().timestamp(),
                                  'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 0}
                        db_p_client.update('object_copies', cp_rec)
                        db_p_client.where(f'id = {task["obj_id"]}')
                        db_p_client.run()
                        c_bucket.rm_object(task['source_bucket'],
                                           task['source_key'])
    return True


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
    #db_client = Database(db_secrets_vals)
    queue_client = SQSHandler(parameters['queue_name'], account, parameters['aws_region'])
    bucket_client = Bucket()
    bucket_resource = RBucket()
    default_target_bucket = 'tna-backup-vault'
    processor = mp.get_context('fork')
    task_queue = processor.Queue()
    processes = []
    while signal_handler.can_run():
        # read sqs queue, update DB and create file copying queue for multi processing
        db_client = Database(db_secrets_vals)
        queue_response = queue_client.receive_message(10)
        if signal_handler.shutdown_requested:
            #print('shutting down')
            for proc in processes:
                proc.close()
            db_client.close()
            sys.exit(0)
        #print('reading message queue')
        if 'Messages' in queue_response:
            task_list = []
            for message in queue_response['Messages']:
                message_body = json.loads(sub_json(message['Body'], regex_set))
                checkin_file_id = message_body['file_id']
                # read queue entry
                db_client.select('queues', ['*'])
                db_client.where(f'message_id = "{message["MessageId"]}"')
                queue_rec = db_client.fetch()
                if not bool(queue_rec):
                    del queue_rec
                    continue
                else:
                    # read checkin entry
                    db_client.select('object_checkins', ['*'])
                    db_client.where(f'id = {checkin_file_id}')
                    checkin_rec = db_client.fetch()
                    if checkin_rec['status'] == 8:  # queue entry is redundant
                        queue_client.delete_message(message['ReceiptHandle'])
                        queue_data = {'status': 8, 'finished_ts': datetime.now().timestamp()}
                        db_client.where(f'file_id = {message_body["file_id"]}')
                        db_client.update('queues', queue_data)
                        db_client.run()
                    else:
                        # get object data
                        obj_info = bucket_client.get_object_info(checkin_rec['bucket'], checkin_rec['object_key'])
                        object_name_parts = deconstruct_path(checkin_rec['object_key'])
                        if obj_info is not None:
                            db_client.select('ap_targets', ['*'])
                            db_client.where(f'access_point = "{object_name_parts["access_point"]}"')
                            ap_rec = db_client.fetch()
                            if ap_rec:
                                s3_target = ap_rec['bucket']
                            else:
                                s3_target = default_target_bucket
                            obj_attr = bucket_client.get_object_attr(checkin_rec['bucket'], checkin_rec['object_key'])
                            # check of any changes
                            # write to table copies
                            tn_split = checkin_rec["object_name"].split('.')
                            if len(tn_split) > 1:
                                target_name = f'{(".").join(tn_split[:-1])}_{str(datetime.now().timestamp()).replace(".", "_")}.{"".join(tn_split[-1:])}'
                            else:
                                target_name = f'{checkin_rec["object_name"]}_{str(datetime.now().timestamp()).replace(".", "_")}'
                            object_copy = {'queue_id': queue_rec['id'], 'checkin_id': checkin_rec['id'],
                                           'object_name': target_name, 'source_name': checkin_rec['object_name'],
                                           'access_point': object_name_parts["access_point"], 'object_size': obj_info['ContentLength'],
                                           'object_type': obj_info['ContentType'],
                                           'etag': obj_info['ETag'].replace('"', ''),
                                           'object_key': checkin_rec['object_key'],
                                           'bucket': s3_target,
                                           'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                           'status': 2,
                                           'percentage': '0.00'}
                            locking_info = {}
                            if "Metadata" in obj_info:
                                obj_metadata = obj_info['Metadata']
                                if find_key_dict("retain_until_date", obj_metadata):
                                    object_copy['retain_until_date'] = obj_metadata['retain_until_date']
                                    locking_info['retain_until_date'] = obj_metadata['retain_until_date']
                                if find_key_dict("lock_mode", obj_metadata):
                                    object_copy['lock_mode'] = obj_metadata['lock_mode']
                                    locking_info['lock_mode'] = obj_metadata['lock_mode']
                                if find_key_dict("legal_hold", obj_metadata):
                                    object_copy['legal_hold'] = obj_metadata['legal_hold']
                                    locking_info['legal_hold'] = obj_metadata['legal_hold']
                                if find_key_dict("lock_until_date", obj_metadata):
                                    object_copy['lock_until_date'] = obj_metadata['lock_until_date']
                                    locking_info['lock_until_date'] = obj_metadata['lock_until_date']
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
                            task_list.append({'file_id': checkin_rec['id'], 'obj_id': obj_id,
                                              'source_bucket': checkin_rec['bucket'], 'source_key': checkin_rec['object_key'],
                                              'access_point': object_name_parts["access_point"], 'target_bucket': s3_target,
                                              'target_obj': f'{object_name_parts["location"]}/{target_name}'.lstrip(
                                                  '/'), 'locking': locking_info
                                              })
            if task_list:
                processes = []
                for task in task_list:
                    task_queue.put(task)
                for i in range(max_pp):
                    processes.append(processor.Process(target=process_object, args=(
                        task_queue, db_secrets_vals, bucket_resource, bucket_client,)))
                    processes[i].start()
                for proc in processes:
                    proc.join()
                for proc in processes:
                    proc.close()
        del queue_response
        db_client.close()


if __name__ == "__main__":
    process_backups()
