import boto3
import botocore.exceptions


class Bucket:
    def __init__(self, bucket: str, object_key: str):
        self.bucket = bucket
        self.object_key = object_key
        self.full_path = ""
        self.location = ""
        self.name = ""
        self.client = boto3.client('s3')
        try:
            self.obj_data = self.client.get_object(Bucket=self.bucket, Key=self.object_key)
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
        self.object_name = self.object_key.split('/')[-1]
        self.location = "/".join(self.object_key.split('/')[:-1])
        self.full_path = self.bucket + "/" + self.object_key,

