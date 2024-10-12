import os
import json
import time
from database.db_mysql import Database
from sqs.sqs import Queue
from s3.s3 import Bucket
from secrets.asm import Secrets
from helper_fx.helpers import set_random_id
from helper_fx.helpers import find_key_dict


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

    recording_ts = time.time()
    random_id = set_random_id(length=128)
    s3_object = Bucket(event_data['bucket']['name'], event_data['object']['key'])
    print(s3_object)
    object_data = {'identifier': random_id, 'bucket': s3_object.bucket, 'object_key': s3_object.object_key,
                   'object_location': s3_object.location, 'object_name': s3_object.object_name,
                   'object_etag': s3_object.obj_data['ETag'].replace('"',''), 'object_size': s3_object.obj_data['ContentLength'],
                   'size_str': str(s3_object.obj_data['ContentLength']), 'object_type': s3_object.obj_data['ContentType'],
                   'recording_ts': str(recording_ts), 'last_modified': s3_object.obj_data['LastModified']}
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

    queue = Queue(queue_url)
    sqs_body = '''\
    {{
        "identifier": "{identifier}"
        "bucket": "{bucket}"
        "object_key": "{object_key}"
        "object_location": "{object_location}"
        "object_name": "{object_name}"
        "object_etag": "{object_etag}"
        "object_size": "{size_str}"
        "object_type": "{object_type}"
        "last_modified": "{last_modified}"
        "recording_ts": "{recording_ts}"
    }}
        '''.format(**object_data)
    del object_data['size_str']
    sqs_results = queue.add(sqs_body, random_id)

    db_secrets = Secrets(asm_id)
    db_secrets_values = json.loads(db_secrets.get_str())
    check_in_db = Database(db_secrets_values)
    check_in_db.insert('checkin_data', object_data)

    check_in_db.close()
