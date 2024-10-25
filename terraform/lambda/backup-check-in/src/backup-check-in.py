import os
import json
from datetime import datetime
from urllib.parse import unquote_plus
from private_tools import Database, Queue, Secrets, Bucket, deconstruct_path
from private_tools import set_random_id, find_key_dict, get_parameters


def lambda_handler(event, context):
    event_data = event['Records'][0]['s3']
    process_object(event_data)
    return {
        'statusCode': 200,
        'body': 'backup-check-in finished for {bucket}/{object}'.format(bucket=event_data['bucket']['name'],
                                                                        object=event_data['object']['key'])
    }


def process_object(event_data):
    received_ts = datetime.now().timestamp()
    ssm_id = os.getenv('SSM_ID')
    parameters = get_parameters(ssm_id, 'eu-west-2')

    db_secrets = Secrets(parameters['asm_id'])
    db_secrets_values = json.loads(db_secrets.get_str())
    check_in_db = Database(db_secrets_values)

    bucket = Bucket(parameters['aws_region'])
    bucket_name = event_data['bucket']['name']
    object_key = unquote_plus(event_data['object']['key'])
    object_path = deconstruct_path(object_key)
    object_name = object_path['object_name']
    object_info = bucket.get_object_info(bucket_name, object_key)
    etag = object_info['ETag'].replace('"', '')
    # neutralise older entries if the object is already in the list but not processed yet
    upd_fields = {'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 8}
    upd_where = f'etag = "{etag}" AND object_key = "{object_key}" AND (status = 3 OR status = 2)'
    check_in_db.update('object_checkins', upd_fields, upd_where)
    # find any entry already in process
    select_where = f'etag = "{etag}" AND object_key = "{object_key}" AND status = 1'
    found_records = check_in_db.select('object_checkins', ['id', 'etag', 'object_key', 'status'], select_where)
    if len(found_records) == 0:
        object_data = {'bucket': bucket_name, 'object_key': object_key,
                       'object_name': object_name, 'etag': etag,
                       'object_size': object_info['ContentLength'], 'object_type': object_info['ContentType'],
                       'last_modified': object_info['LastModified'], 'received_ts': received_ts,
                       'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 3}
        if "Metadata" in object_info:
            obj_metadata = object_info['Metadata']
            if find_key_dict("retention_period", obj_metadata):
                object_data['retention_period'] = obj_metadata['retention_period']
            if find_key_dict("lock_mode", obj_metadata):
                object_data['lock_mode'] = obj_metadata['lock_mode']
            if find_key_dict("legal_hold", obj_metadata):
                object_data['legal_hold'] = obj_metadata['legal_hold']
            if find_key_dict("lock-until-date", obj_metadata):
                object_data['lock_until_date'] = obj_metadata['lock-until-date']
            if 'ChecksumCRC32' in object_info:
                object_data['checksum_crc32'] = object_info['ChecksumCRC32']
            if 'ChecksumCRC32C' in object_info:
                object_data['checksum_crc32c'] = object_info['ChecksumCRC32C']
            if 'ChecksumSHA1' in object_info:
                object_data['checksum_sha1'] = object_info['ChecksumSHA1']
            if 'ChecksumSHA256' in object_info:
                object_data['checksum_sha256'] = object_info['ChecksumSHA256']
        file_id = check_in_db.insert('object_checkins', object_data)
        object_data['file_id'] = file_id
        size_str = str(object_info['ContentLength'])

        queue = Queue(parameters['queue_url'])
        sqs_body = f'''\
        {{
            "file_id": "{file_id}"
            "bucket": "{bucket_name}"
            "object_key": "{object_key}"
            "object_name": "{object_name}"
            "etag": "{etag}"
            "object_size": "{size_str}"
            "object_type": "{object_info['ContentType']}"
            "last_modified": "{object_info['ResponseMetadata']['HTTPHeaders']['last-modified']}"
            "created_at": "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }}
        '''
        sqs_results = queue.add(sqs_body, set_random_id())
        queue_data = {'message_id': sqs_results['MessageId'], 'sequence_number': sqs_results['SequenceNumber'],
                      'received_ts': datetime.now().timestamp(),
                      'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                      'status': 2, 'file_id': file_id}
        if 'MD5OfMessageBody' in sqs_results:
            queue_data['md5_of_message_body'] = sqs_results['MD5OfMessageBody']
        if 'MD5OfMessageAttributes' in sqs_results:
            queue_data['md5_of_message_attributes'] = sqs_results['MD5OfMessageAttributes']
        if 'MD5OfMessageSystemAttributes' in sqs_results:
            queue_data['md5_of_message_system_attributes'] = sqs_results['MD5OfMessageSystemAttributes']
        queue_id = check_in_db.insert('queues', queue_data)
        object_data = {'queue_id': queue_id, 'status': 2,
                       'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       'finished_ts': datetime.now().timestamp()}
        where_clause = 'id = ' + str(file_id)
        check_in_db.update('object_checkins', object_data, where_clause)
    else:
        object_data = {'bucket': bucket_name, 'object_key': object_key,
                       'object_name': object_name, 'etag': etag,
                       'object_size': object_info['ContentLength'], 'object_type': object_info['ContentType'],
                       'last_modified': object_info['ResponseMetadata']['HTTPHeaders']['last-modified'],
                       'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 7}
        if "Metadata" in object_info:
            obj_metadata = object_info['Metadata']
            if find_key_dict("retention_period", obj_metadata):
                object_data['retention_period'] = obj_metadata['retention_period']
            if find_key_dict("lock_mode", obj_metadata):
                object_data['lock_mode'] = obj_metadata['lock_mode']
            if find_key_dict("legal_hold", obj_metadata):
                object_data['legal_hold'] = obj_metadata['legal_hold']
            if find_key_dict("lock-until-date", obj_metadata):
                object_data['lock_until_date'] = obj_metadata['lock-until-date']
            if 'ChecksumCRC32' in object_info:
                object_data['checksum_crc32'] = object_info['ChecksumCRC32']
            if 'ChecksumCRC32C' in object_info:
                object_data['checksum_crc32c'] = object_info['ChecksumCRC32C']
            if 'ChecksumSHA1' in object_info:
                object_data['checksum_sha1'] = object_info['ChecksumSHA1']
            if 'ChecksumSHA256' in object_info:
                object_data['checksum_sha256'] = object_info['ChecksumSHA256']
        file_id = check_in_db.insert('object_checkins', object_data)

    check_in_db.close()
