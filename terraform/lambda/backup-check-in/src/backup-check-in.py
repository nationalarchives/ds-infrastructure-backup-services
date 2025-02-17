import os
import json
from datetime import datetime
from urllib.parse import unquote_plus
from private_tools import Database, Queue, Secrets, Bucket
from private_tools import set_random_id, get_ssm_parameters, deconstruct_path
from private_tools import find_value_dict


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
    parameters = get_ssm_parameters(ssm_id, 'eu-west-2')

    db_secrets = Secrets(parameters['asm_id'])
    db_secrets_values = json.loads(db_secrets.get_secrets())
    check_in_db = Database(db_secrets_values)

    s3_obj = Bucket(region=parameters['aws_region'])
    obj_key = unquote_plus(event_data['object']['key'])
    object_path = deconstruct_path(unquote_plus(event_data['object']['key']))
    object_name = object_path['object_name']
    obj_info = s3_obj.get_object_info(bucket=event_data['bucket']['name'], key=obj_key)
    if obj_info is None:
        checkin_rec = {'bucket': event_data['bucket']['name'], 'object_key': obj_key,
                       'object_name': object_name, 'received_ts': received_ts,
                       'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 9}
        check_in_db.insert('object_checkins', checkin_rec)
        checkin_id = check_in_db.run()
        check_in_db.close()
        print(f"object doesn't exist - object_checkins id: {checkin_id}")
        return
    # neutralise older entries if the object is already in the list but not queued or in progress
    upd_fields = {'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  'finished_ts': datetime.now().timestamp(), 'status': 4}
    check_in_db.where(f'object_key = "{obj_key}" AND status = 0')
    check_in_db.update('object_checkins', upd_fields)
    check_in_db.run()
    # find any entry in progress
    check_in_db.where(f'object_key = "{obj_key}" AND status = 1')
    check_in_db.select('object_checkins', ['id', 'etag', 'object_key', 'status'])
    found_records = check_in_db.run()
    if len(found_records) > 0:
        checkin_rec = {'bucket': event_data['bucket']['name'], 'object_key': obj_key,
                       'object_name': object_name, 'received_ts': received_ts,
                       'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 5}
        check_in_db.insert('object_checkins', checkin_rec)
        checkin_id = check_in_db.run()
        check_in_db.close()
        print(f'object entry already in db: {checkin_id}:{event_data["bucket"]["name"]}/{obj_key}/{object_name}')
        return
    checkin_rec = {'bucket': event_data['bucket']['name'], 'object_key': obj_key, 'object_name': object_name,
                   'etag': obj_info['etag'], 'object_size': obj_info['content_length'],
                   'object_type': obj_info['content_type'], 'last_modified': obj_info['last_modified'],
                   'received_ts': received_ts, 'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 0,
                   'storage_class': find_value_dict("storage_class", obj_info),
                   'expiration_period': find_value_dict('expiration_period', obj_info),
                   'retention_period': find_value_dict('retention_period', obj_info),
                   'lock_mode': find_value_dict('lock_mode', obj_info),
                   'legal_hold': find_value_dict('legal_hold', obj_info),
                   'serverside_encryption': find_value_dict('serverside_encryption', obj_info),
                   'sse_customer_algorithm': find_value_dict('sse_customer_algorithm', obj_info),
                   'sse_customer_key_md5': find_value_dict('sse_customer_key_md5', obj_info),
                   'sse_kms_key_id': find_value_dict('sse_kms_key_id', obj_info)}
    check_in_db.insert('object_checkins', checkin_rec)
    checkin_id = check_in_db.run()
    obj_info['checkin_id'] = checkin_id
    size_str = str(obj_info['content_length'])
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
    print(f'object added to queue: {checkin_id}')
    queue_data = {'message_id': sqs_results['MessageId'],
                  'checkin_id': checkin_id, 'status': 0,
                  'sequence_number': sqs_results['SequenceNumber'],
                  'received_ts': datetime.now().timestamp(),
                  'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    if 'MD5OfMessageBody' in sqs_results:
        queue_data['md5_of_message_body'] = sqs_results['MD5OfMessageBody']
    if 'MD5OfMessageAttributes' in sqs_results:
        queue_data['md5_of_message_attributes'] = sqs_results['MD5OfMessageAttributes']
    if 'MD5OfMessageSystemAttributes' in sqs_results:
        queue_data['md5_of_message_system_attributes'] = sqs_results['MD5OfMessageSystemAttributes']
    check_in_db.insert('queues', queue_data)
    queue_id = check_in_db.run()
    object_data = {'queue_id': queue_id,
                   'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   'finished_ts': datetime.now().timestamp()}
    check_in_db.where(f'id = {str(checkin_id)}')
    check_in_db.update('object_checkins', object_data)
    check_in_db.run()
    check_in_db.close()
