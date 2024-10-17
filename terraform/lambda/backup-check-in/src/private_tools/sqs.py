import boto3
import botocore.exceptions
from pyasn1.type.univ import Boolean


class Queue:
    def __init__(self, queue_location):
        self.queue_url = queue_location
        self.queue_client = boto3.client('sqs')

    def add(self, msg_body: str, dedup_id: str):
        try:
            response = self.queue_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=msg_body,
                MessageGroupId="lambda-check-in",
                MessageDeduplicationId=dedup_id
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'InvalidMessageContents ':
                print('SQS - InvalidMessageContents')
            elif error.response['Error']['Code'] == 'UnsupportedOperation ':
                print('SQS - UnsupportedOperation')
            elif error.response['Error']['Code'] == 'RequestThrottled ':
                print('SQS - RequestThrottled')
            elif error.response['Error']['Code'] == 'QueueDoesNotExist ':
                print('SQS - QueueDoesNotExist')
            elif error.response['Error']['Code'] == 'InvalidSecurity ':
                print('SQS - InvalidSecurity')
            elif error.response['Error']['Code'] == 'InvalidAddress ':
                print('SQS - InvalidAddress')
            else:
                print('SQS - unknown error')
            raise error
        else:
            return response

    def delete_message(self, handle: str) -> bool:
        self.queue_client.delete_message(QueueUrl=self.queue_url,
                        ReceiptHandle=handle)
        return True

    def poll(self):
        pass
