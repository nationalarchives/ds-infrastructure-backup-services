import boto3
import botocore.exceptions


class Queue:
    def __init__(self, queue_location):
        self.queue_url = queue_location
        self.queue_client = boto3.client('sqs')

    def add(self, msg_body):
        try:
            response = self.queue_client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=msg_body)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'InvalidMessageContents ':
                print('SQS - InvalidMessageContents')
            if error.response['Error']['Code'] == 'UnsupportedOperation ':
                print('SQS - UnsupportedOperation')
            if error.response['Error']['Code'] == 'RequestThrottled ':
                print('SQS - RequestThrottled')
            if error.response['Error']['Code'] == 'QueueDoesNotExist ':
                print('SQS - QueueDoesNotExist')
            if error.response['Error']['Code'] == 'InvalidSecurity ':
                print('SQS - InvalidSecurity')
            if error.response['Error']['Code'] == 'InvalidAddress ':
                print('SQS - InvalidAddress')
            else:
                return response

    def delete_message(self):
        pass

    def poll(self):
        pass

