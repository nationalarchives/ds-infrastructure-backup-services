import boto3
import json
import os, sys
import time
from datetime import datetime
from private_tools import SignalHandler, SQSHandler, Database, Secrets, get_parameters


def send_queue_metrics(sqs_queue, dbc):
    queue_attribs = sqs_queue.get_attributes()
    queue_name: str = queue_attribs['Attributes']['QueueArn'].split(":")[-1]
    queue_length: int = queue_attribs['Attributes']['ApproximateNumberOfMessages']
    if queue_length > 0:
        queue_rec = {'queue_name': queue_name, 'queue_length': queue_length,
                     'queue_arn': queue_attribs['Attributes']['QueueArn'],
                     'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     'status': 0}
        dbc.insert('queue_status', queue_rec)
        dbc.run()

def queue_monitor():
    ssm_id = os.getenv('SSM_ID')
    parameters = get_parameters(ssm_id, 'eu-west-2')

    signal_handler = SignalHandler()
    interval = 10
    client = boto3.client('sts')
    response = client.get_caller_identity()
    account = response['Account']
    db_secrets = Secrets(parameters['asm_id'])
    db_secrets_vals = json.loads(db_secrets.get_secrets())
    queue_client = SQSHandler(parameters['queue_name'], account, parameters['aws_region'])
    dl_queue_client = SQSHandler(parameters['dl_queue_name'], account, parameters['aws_region'])
    db_client = Database(db_secrets_vals)
    while signal_handler.can_run():
        if signal_handler.shutdown_requested:
            sys.exit(0)
        send_queue_metrics(queue_client, db_client)
        send_queue_metrics(dl_queue_client, db_client)
        if signal_handler.shutdown_requested:
            sys.exit(0)
        time.sleep(interval)
    db_client.close()


if __name__ == "__main__":
    queue_monitor()
