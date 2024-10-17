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
            message_body = json.loads(message['Body'])
            print(message_body)
            db.select('queues', ['*'])
            db.where('message_id = ' + message['MessageId'])
            q_rec = db.fetch()
            if not q_rec:
                print(f'Error message not found - id {message["MessageId"]}')

            object_copy = {'checkin_id': message_body['file_id'], 'target_bucket': message_body['bucket'],
                           'object_name': message_body['object_name'], 'target_name': message_body['target_name'],
                           'object_key': message_body['object_key'], 'object_size': message_body['object_size'],
                           'object_type': message_body['object_type'], 'created_at': str(datetime.now())[0:19],
                           'etag': message_body['etag'], 'status': 2}
            db.insert('object_copies', object_copy)
            queue.delete_message(message['ReceiptHandle'])
    db.close()


if __name__ == "__main__":
    process_backups()
