import boto3
import botocore.exceptions


class Bucket:
    def __init__(self, region: str='eu-west-2'):
        self.client = boto3.client('s3',
                                   region_name=region)

    def get_object_info(self, bucket: str, object_key: str):
        try:
            obj_data = self.client.get_object(Bucket=bucket,
                                              Key=object_key)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchKey':
                print('S3 - NoSuchKey')
            elif error.response['Error']['Code'] == 'InvalidObjectState':
                print('S3 - InvalidObjectState')
            else:
                print('S3 - unknown error')
            raise error
        else:
            return obj_data

    def get_object_attr(self, bucket: str, object_key):
        try:
            obj_attr = self.client.get_object_attributes(Bucket=bucket,
                                                         Key=object_key,
                                                         ObjectAttributes=[
                                                             'Checksum',
                                                             'ETag',
                                                             'StorageClass',
                                                             'ObjectSize']
                                                         )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchKey':
                print('S3 - NoSuchKey')
            elif error.response['Error']['Code'] == 'InvalidObjectState':
                print('S3 - InvalidObjectState')
            else:
                print('S3 - unknown error')
            raise error
        else:
            return obj_attr

    def copy_object(self, source_bucket, source_key, target_bucket, target_key):
        try:
            response = self.client.copy_object(CopySource={'Bucket': source_bucket, 'Key': source_key},
                                               Bucket=target_bucket, Key=target_key)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ObjectNotInActiveTierError':
                print('S3 - ObjectNotInActiveTierError')
            else:
                raise error
        else:
            return response
