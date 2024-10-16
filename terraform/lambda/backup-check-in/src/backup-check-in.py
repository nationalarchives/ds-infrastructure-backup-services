import os
import json
from datetime import datetime
from urllib.parse import unquote_plus
from private_tools import Database, Queue, Secrets, Bucket
from private_tools import set_random_id, find_key_dict


def lambda_handler(event, context):
    event_data = event['Records'][0]['s3']
    process_object(event_data)
    return {
        'statusCode': 200,
        'body': 'backup-check-in finished for {bucket}/{object}'.format(bucket=event_data['bucket']['name'], object=event_data['object']['key'])
    }


def process_object(event_data):
    queue_url = os.getenv('QUEUE_URL')
    asm_id = os.getenv('ASM_ID')

    print(event_data)
    trigger_ts = datetime.now().timestamp()
    unique_name_sufix = str(trigger_ts).replace('.', '_')
    created_at = str(datetime.now())[0:19]
    s3_object = Bucket(event_data['bucket']['name'], unquote_plus(event_data['object']['key']))

    db_secrets = Secrets(asm_id)
    db_secrets_values = json.loads(db_secrets.get_str())
    check_in_db = Database(db_secrets_values)

    base_name_lst = s3_object.object_name.split('.')
    if len(base_name_lst) == 1:
        target_name = s3_object.object_name + unique_name_sufix
    else:
        target_name = '.'.join(base_name_lst[:-1]) + '_' + unique_name_sufix + '.' + str(base_name_lst[-1])

    object_data = {'bucket': s3_object.bucket, 'object_key': s3_object.object_key,
                   'object_name': s3_object.object_name, 'target_name': target_name,
                   'etag': s3_object.obj_data['ETag'].replace('"',''), 'object_size': s3_object.obj_data['ContentLength'],
                   'object_type': s3_object.obj_data['ContentType'], 'created_at': created_at, 'status': 2}
    if "ResponseMetadata" in s3_object.obj_data:
        object_data['last_modified'] = s3_object.obj_data['ResponseMetadata']['HTTPHeaders']['last-modified']
    else:
        object_data['last_modified'] = 'unknown'
    if "Metadata" in s3_object.obj_data:
        obj_metadata = s3_object.obj_data['Metadata']
        if find_key_dict("retention_period", obj_metadata):
            object_data['retention_period'] = obj_metadata['retention_period']
        if find_key_dict("lock_mode", obj_metadata):
            object_data['lock_mode'] = obj_metadata['lock_mode']
        if find_key_dict("legal_hold", obj_metadata):
            object_data['legal_hold'] = obj_metadata['legal_hold']
        if find_key_dict("lock-until-date", obj_metadata):
            object_data['lock_until_date'] = obj_metadata['lock-until-date']
    if 'Checksum' in s3_object.obj_attr:
        object_checksum = s3_object.obj_attr['Checksum']
        if 'ChecksumCRC32' in  object_checksum:
            object_data['checksum_crc32'] = object_checksum['ChecksumCRC32']
        if 'ChecksumCRC32C' in  object_checksum:
            object_data['checksum_crc32c'] = object_checksum['ChecksumCRC32C']
        if 'ChecksumSHA1' in  object_checksum:
            object_data['checksum_sha1'] = object_checksum['ChecksumSHA1']
        if 'ChecksumSHA256' in  object_checksum:
            object_data['checksum_sha256'] = object_checksum['ChecksumSHA256']
    file_id = check_in_db.insert('object_checkins', object_data)
    object_data['file_id'] = file_id
    object_data['size_str'] = str(s3_object.obj_data['ContentLength'])

    queue = Queue(queue_url)
    sqs_body = '''\
    {{
        "file_id": "{file_id}"
        "bucket": "{bucket}"
        "object_key": "{object_key}"
        "object_name": "{object_name}"
        "target_name": "{target_name}"
        "etag": "{etag}"
        "object_size": "{size_str}"
        "object_type": "{object_type}"
        "last_modified": "{last_modified}"
        "created_at": "{created_at}"
    }}
        '''.format(**object_data)
    sqs_results = queue.add(sqs_body, set_random_id())

    created_at = str(datetime.now())[0:19]
    queue_data = {'message_id': sqs_results['MD5OfMessageBody'], 'sequence_number': sqs_results['SequenceNumber'],
                  'created_at': created_at, 'status': 2, 'file_id': file_id}
    if 'MD5OfMessageBody' in sqs_results:
        queue_data['md5_of_message_body'] = sqs_results['MD5OfMessageBody']
    if 'MD5OfMessageAttributes' in sqs_results:
        queue_data['md5_of_message_attributes'] = sqs_results['MD5OfMessageAttributes']
    if 'MD5OfMessageSystemAttributes' in sqs_results:
        queue_data['md5_of_message_system_attributes'] = sqs_results['MD5OfMessageSystemAttributes']
    queue_id = check_in_db.insert('queues', queue_data)
    updated_at = str(datetime.now())[0:19]
    object_data = {"queue_id": queue_id, "updated_at": updated_at}
    where_clause = 'id = ' + str(file_id)
    check_in_db.update('object_checkins',  object_data, where_clause)

    check_in_db.close()
