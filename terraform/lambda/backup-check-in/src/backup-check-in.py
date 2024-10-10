import os
import json
from database.db_mysql import Database
from queue.sqs import Queue
from s3.s3 import Bucket
from secrets.asm import Secrets
import helper_fx


def lambda_handler(event, context):
    event_data = event['Records'][0]['s3']
    process_object(event_data)
    return {
        'message': 'backup-check-in finished'
    }


def process_object(event_data):
    queue_url = os.getenv('QUEUE_URL')
    asm_id = os.getenv('ASM_ID')

    random_id = helper_fx.set_random_id()
    db_secrets = Secrets(asm_id)

    s3_object = Bucket(event_data['bucket']['name'], event_data['object']['key'])
    object_info = s3_object.get_object_info()
    object_info['identifier'] = random_id()
    object_info['bucket'] = s3_object['bucket']
    object_info['key'] = s3_object['key']
    object_info['location'] = s3_object['location']
    object_info['object_name'] = s3_object['object_name']
    object_info['size'] = s3_object['ContentLength']
    object_info['size_str'] = str(s3_object['ContentLength'])
    object_info['type'] = s3_object['ContentType']
    if "ResponseMetadata" in s3_object:
        object_info['last_modified'] = s3_object['ResponseMetadata']['HTTPHeaders']['last-modified']
        object_info['response_metadata_str'] = json.dumps(s3_object['ResponseMetadata'], default=str)
    if "Metadata" in s3_object:
        obj_metadata = s3_object['Metadata']
        if helper_fx.find_key_dict("retention_period", obj_metadata):
            object_info['retention'] = obj_metadata['retention_period']
        else:
            object_info['retention'] = ''
        if helper_fx.find_key_dict("lockmode", obj_metadata):
            object_info['lock_mode'] = obj_metadata['lock_mode']
        else:
            object_info['lock_mode'] = ''
        if helper_fx.find_key_dict("legal_hold", obj_metadata):
            object_info['legal_hold'] = obj_metadata['legal_hold']
        else:
            object_info['legal_hold'] = ''
        if helper_fx.find_key_dict(obj_metadata, "lock-until-date"):
            object_info['lock_until_date'] = obj_metadata['lock-until-date']
        else:
            object_info['lock_until_date'] = ''
        object_info['metadata_str'] = json.dumps(s3_object['MetaData'], default=str)

    queue = Queue(queue_url)
    sqs_body = '''\
    {{
        "identifier": "{identifier}"
        "bucket": "{bucket}"
        "etag": "{ETag}"
        "size": "{size_str}"
        "type": "{type}"
        "last_modified": "{last_modified}"
    }}
        '''.format(**object_info)
    sqs_results = queue.add(sqs_body)

    del object_info['size_str']

    check_in_db = Database(db_secrets.get_json())
    check_in_db.insert('sqs_log', object_info)

    check_in_db.close()
