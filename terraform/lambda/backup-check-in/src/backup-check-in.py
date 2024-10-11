import os
import json
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

    random_id = set_random_id(length=128)
    s3_object = Bucket(event_data['bucket']['name'], event_data['object']['key'])
    object_data = {'identifier': random_id, 'bucket': s3_object.bucket, 'key': s3_object.key,
                   'location': s3_object.location, 'object_name': s3_object.object_name,
                   'etag': s3_object.object_data['ETag'], 'size': s3_object.obj_data['ContentLength'],
                   'size_str': str(s3_object.obj_data['ContentLength']), 'type': s3_object.obj_data['ContentType']}
    if "ResponseMetadata" in s3_object.obj_data:
        object_data['last_modified'] = s3_object.obj_data['ResponseMetadata']['HTTPHeaders']['last-modified']
        object_data['response_metadata_str'] = json.dumps(s3_object.obj_data['ResponseMetadata'], default=str)
    if "Metadata" in s3_object.obj_data:
        obj_metadata = s3_object.obj_data['Metadata']
        if find_key_dict("retention_period", obj_metadata):
            object_data['retention'] = obj_metadata['retention_period']
        if find_key_dict("lockmode", obj_metadata):
            object_data['lock_mode'] = obj_metadata['lock_mode']
        if find_key_dict("legal_hold", obj_metadata):
            object_data['legal_hold'] = obj_metadata['legal_hold']
        if find_key_dict("lock-until-date", obj_metadata):
            object_data['lock_until_date'] = obj_metadata['lock-until-date']
        object_data['metadata_str'] = json.dumps(s3_object.obj_data['Metadata'], default=str)

    queue = Queue(queue_url)
    sqs_body = '''\
    {{
        "identifier": "{identifier}"
        "bucket": "{bucket}"
        "key": "{key}"
        "location": "{location}"
        "object_name": "{object_name}"
        "etag": "{etag}"
        "size": "{size_str}"
        "type": "{type}"
        "last_modified": "{last_modified}"
    }}
        '''.format(**object_data)
    sqs_results = queue.add(sqs_body, random_id)

    del object_data['size_str']

    db_secrets = Secrets(asm_id)
    db_secrets_values = json.loads(db_secrets.get_str())
    print(type(db_secrets_values))
    check_in_db = Database(db_secrets_values)
    check_in_db.insert('sqs_log', object_data)

    check_in_db.close()
