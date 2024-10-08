import boto3
import botocore.exceptions


class Bucket:
    def __init__(self, bucket: str, key: str):
        self.bucket = bucket
        self.key = key
        self.full_path = ""
        self.location = ""
        self.object_name = ""
        self.client = boto3.client('s3')
        try:
            self.obj_data = self.client.get_object(Bucket=self.bucket, Key=self.key)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchKey':
                print('S3 - NoSuchKey')
            elif error.response['Error']['Code'] == 'InvalidObjectState':
                print('S3 - InvalidObjectState')
            else:
                print('S3 - unknown error')
            raise error
        else:
            self.deconstruct_path()

    def get_object_info(self):
        return self.obj_data

    def deconstruct_path(self):
        self.location = self.key.split('/')[-1]
        self.object_name = "/".join(self.key.split('/')[:-1])
        self.full_path = self.bucket + "/" + self.key,

