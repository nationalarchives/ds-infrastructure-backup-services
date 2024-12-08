import os
import json
from datetime import datetime
from dateutil.tz import tzutc
from urllib.parse import unquote_plus
from private_tools import Database, Queue, Secrets, s3_object
from private_tools import set_random_id, get_parameters, deconstruct_path


def lambda_handler(event, context):
    event_data = event['Records'][0]['s3']
    process_object(event_data)
    return {
        'statusCode': 200,
        'body': f'backup-check-in finished for {event_data["bucket"]["name"]}/{event_data["object"]["key"]}'
    }


def process_object(event_data):
    received_ts = datetime.now().timestamp()
    ssm_id = os.getenv('SSM_ID')
    parameters = get_parameters(ssm_id, 'eu-west-2')

    db_secrets = Secrets(parameters['asm_id'])
    db_secrets_values = json.loads(db_secrets.get_str())
    check_in_db = Database(db_secrets_values)

    s3_obj = s3_object(region=parameters['aws_region'])
    obj_key = unquote_plus(event_data['object']['key'])
    obj_info = s3_obj.info(bucket=event_data['bucket']['name'], key=obj_key)
    object_path = deconstruct_path(unquote_plus(event_data['object']['key']))
    object_name = object_path['object_name']
    # neutralise older entries if the object is already in the list but not processed yet
    upd_fields = {'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  'finished_ts': datetime.now().timestamp(),
                  'status': 3}
    upd_where = f'etag = "{obj_info["etag"]}" AND object_key = "{obj_key}" AND status = 0'
    check_in_db.update('object_checkins', upd_fields, upd_where)
    # find any entry already in process
    checkin_status = 0
    select_where = f'etag = "{obj_info["etag"]}" AND object_key = "{obj_key}" AND status = 1'
    found_records = check_in_db.select('object_checkins', ['id', 'etag', 'object_key', 'status'], select_where)
    if len(found_records) > 0:
        checkin_status = 5
    # find already
    select_where = f'etag = "{obj_info["etag"]}" AND object_key = "{obj_key}" AND status = 0'
    found_records = check_in_db.select('object_checkins', ['id', 'etag', 'object_key', 'status'], select_where)
    if len(found_records) > 0:
        checkin_status = 3
    checkin_rec = {'bucket': event_data['bucket']['name'], 'object_key': obj_key,
                   'object_name': object_name, 'etag': obj_info['etag'],
                   'object_size': obj_info['object_size'], 'object_type': obj_info['content_type'],
                   'last_modified': obj_info['last_modified'], 'received_ts': received_ts,
                   'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': checkin_status}
    if 'retain_until_date' in obj_info:
        checkin_rec['retain_until_date'] = obj_info['retain_until_date']
    if 'lock_mode' in obj_info:
        checkin_rec['lock_mode'] = obj_info['lock_mode']
    if 'legal_hold' in obj_info:
        checkin_rec['legal_hold'] = obj_info['legal_hold']
    if 'checksum_crc32' in obj_info:
        checkin_rec['checksum_crc32'] = obj_info['checksum_crc32']
    if 'checksum_crc32c' in obj_info:
        checkin_rec['checksum_crc32c'] = obj_info['checksum_crc32c']
    if 'checksum_sha1' in obj_info:
        checkin_rec['checksum_sha1'] = obj_info['checksum_sha1']
    if 'checksum_sha256' in obj_info:
        checkin_rec['checksum_sha256'] = obj_info['checksum_sha256']
    checkin_id = check_in_db.insert('object_checkins', checkin_rec)
    if checkin_status == 0:
        obj_info['checkin_id'] = checkin_id
        size_str = str(obj_info['object_size'])

        queue = Queue(parameters['queue_url'])
        sqs_body = f'''\
        {{
            "checkin_id": "{checkin_id}"
            "bucket": "{event_data['bucket']['name']}"
            "object_key": "{obj_key}"
            "object_name": "{object_name}"
            "etag": "{obj_info['etag']}"
            "object_size": "{size_str}"
            "object_type": "{obj_info['content_type']}"
            "last_modified": "{obj_info['last_modified']}"
            "created_at": "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }}
        '''
        sqs_results = queue.add(sqs_body, set_random_id())
        queue_data = {'message_id': sqs_results['MessageId'], 'sequence_number': sqs_results['SequenceNumber']}
        if 'MD5OfMessageBody' in sqs_results:
            queue_data['md5_of_message_body'] = sqs_results['MD5OfMessageBody']
        if 'MD5OfMessageAttributes' in sqs_results:
            queue_data['md5_of_message_attributes'] = sqs_results['MD5OfMessageAttributes']
        if 'MD5OfMessageSystemAttributes' in sqs_results:
            queue_data['md5_of_message_system_attributes'] = sqs_results['MD5OfMessageSystemAttributes']
    else:
        queue_data = {'message_id': None, 'sequence_number': None}
    queue_data['received_ts'] = datetime.now().timestamp()
    queue_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    queue_data['status'] = checkin_status
    queue_data['checkin_id'] = checkin_id
    queue_id = check_in_db.insert('queues', queue_data)
    if checkin_status == 0 or checkin_status == 2:
        update_status = 2
    else:
        update_status = checkin_status
    object_data = {'queue_id': queue_id, 'status': update_status,
                   'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   'finished_ts': datetime.now().timestamp()}
    where_clause = 'id = ' + str(checkin_id)
    check_in_db.update('object_checkins', object_data, where_clause)
    check_in_db.close()
