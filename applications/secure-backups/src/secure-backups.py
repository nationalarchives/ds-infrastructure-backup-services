import boto3
import json
import os
from datetime import datetime
from private_tools import SignalHandler, SQSHandler, Database, Secrets


def process_backups():
    signal_handler = SignalHandler()
    queue_url = os.getenv('QUEUE_URL')
    asm_id = os.getenv('ASM_ID')
    client = boto3.client('sts')
    response = client.get_caller_identity()
    account = response['Account']
    db_secrets = Secrets(asm_id)
    db_secrets_values = json.loads(db_secrets.get_str())

    queue = SQSHandler(queue_url, account)
    db = Database(db_secrets_values)

    while signal_handler.can_run():
        queue_response = queue.receive_message()
        for message in queue_response['Messages']:
            added_ts = datetime.now().timestamp()
            message_id = message['MessageId']
            receipt_handler = message['ReceiptHandle']
            message_body = json.loads(message['Body'])
            md5_of_body = message['MD5OfBody']
            db.select('queues', ['*'])
            db.where('message_id = ' + message['MessageId'])
            q_rec = db.fetch()
            if not q_rec:
                print(f'Error message not found - id {message_id}')
            queue = {}
            file_id = message_body['file_id']
            bucket = message_body['bucket']
            object_key = message_body['object_key']
            object_name = message_body['object_name']
            etag = message_body['etag']
            object_size = message_body['object_size']
            object_type = message_body['object_type']
            last_modified = message_body['last_modified']
            created_at = message_body['created_at']

            object_copy = {'checkin_id': message_body['file_id'], 'target_bucket': message_body['bucket'],
                           'object_name': message_body['object_name'], 'target_name': message_body['target_name'],
                           'object_key': message_body['object_key'], 'object_size': message_body['object_size'],
                           'object_type': message_body['object_type'],
                           'etag': message_body['etag']}
            print(message_body)

    db.close()


if __name__ == "__main__":
    process_backups()
