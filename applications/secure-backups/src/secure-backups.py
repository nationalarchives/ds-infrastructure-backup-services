import boto3
import json
import os
from sighandler.sighandler import SignalHandler
from queuehandler.sqs import SQSHandler
from database.db_mysql import Database
from secrets.asm import Secrets


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
            message_id = message['MessageId']
            receipt_handler = message['ReceiptHandle']
            message_body = json.loads(message['Body'])
            md5_of_body = message['MD5OfBody']

            file_id = message_body['file_id']
            bucket = message_body['bucket']
            object_key = message_body['object_key']
            object_name = message_body['object_name']
            etag = message_body['etag']
            object_size = message_body['object_size']
            object_type = message_body['object_type']
            last_modified = message_body['last_modified']
            created_at = message_body['created_at']

            print(message_body)


if __name__ == "__main__":
    process_backups()
