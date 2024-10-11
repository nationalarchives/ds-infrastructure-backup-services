import boto3
import botocore.exceptions
import json


class Secrets:
    def __init__(self, secret_name: str):
        self.client = boto3.client('secretsmanager')
        self.secret_name = secret_name
        print(self.secret_name)

    def get_json(self):
        try:
            sm_response = self.client.get_secret_value(SecretId=self.secret_name)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                print('ASM - ResourceNotFoundException')
            elif error.response['Error']['Code'] == 'InvalidParameterException':
                print('ASM - InvalidParameterException')
            elif error.response['Error']['Code'] == 'InvalidRequestException':
                print('ASM - InvalidRequestException')
            elif error.response['Error']['Code'] == 'DecryptionFailure':
                print('ASM - DecryptionFailure')
            elif error.response['Error']['Code'] == 'InternalServiceError':
                print('ASM - InternalServiceError')
            else:
                print('ASM - unknown error')
            raise error
        else:
            print(sm_response)
            return json.loads(sm_response['SecretString'])
