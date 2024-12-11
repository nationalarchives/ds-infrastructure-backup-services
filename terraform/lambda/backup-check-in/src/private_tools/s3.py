import boto3
import botocore.exceptions
from datetime import datetime
from dateutil.tz import tzutc
from .helpers import find_key_dict, find_value_dict


class Bucket:
    def __init__(self, region):
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
        return response


class s3_object:
    def __init__(self, *, region: str):
        self.client = boto3.client('s3',
                                   region_name=region)

    def info(self, *, bucket: str, key: str):
        try:
            obj_get = self.client.get_object(Bucket=bucket, Key=key, Range='bytes=0-0')
            obj_attr = self.client.get_object_attributes(Bucket=bucket, Key=key,
                                                         ObjectAttributes=['Checksum',
                                                                           'StorageClass',
                                                                           'ObjectSize'])
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchKey':
                print('S3 - NoSuchKey')
                return None
            else:
                print('S3 - unknown error')
                raise error
        obj_info = {'bucket_name': bucket, 'object_key': key,
                    'last_modified': obj_get['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    'object_size': obj_attr['ObjectSize'],
                    'etag': obj_get['ETag'].replace('"', ''),
                    'content_type': obj_get['ContentType'],
                    'serverside_encryption': obj_get['ServerSideEncryption'], }
        if "ExpiresString" in obj_get:
            obj_info['expires_string'] = obj_get['ExpiresString']
        if "SSECustomerAlgorithm" in obj_get:
            obj_info['sse_customer_algorithm'] = obj_get['SSECustomerAlgorithm']
        if "SSECustomerKeyMD5" in obj_get:
            obj_info['sse_customer_key_md5'] = obj_get['SSECustomerKeyMD5']
        if "SSEKMSKeyId" in obj_get:
            obj_info['sse_kms_key_id'] = obj_get['SSEKMSKeyId']
        if "Metadata" in obj_get:
            if find_value_dict("retain_until_date", obj_get['Metadata']):
                obj_info['retain_until_date'] = obj_get['Metadata']['retain_until_date']
            if find_value_dict("lock_mode", obj_get['Metadata']):
                obj_info['lock_mode'] = obj_get['Metadata']['lock_mode']
            if find_value_dict("legal_hold", obj_get['Metadata']):
                obj_info['legal_hold'] = obj_get['Metadata']['legal_hold']
        if 'ChecksumCRC32' in obj_info:
            obj_info['checksum_crc32'] = obj_attr['ChecksumCRC32']
        if 'ChecksumCRC32C' in obj_info:
            obj_info['checksum_crc32c'] = obj_attr['ChecksumCRC32C']
        if 'ChecksumSHA1' in obj_info:
            obj_info['checksum_sha1'] = obj_attr['ChecksumSHA1']
        if 'ChecksumSHA256' in obj_info:
            obj_info['checksum_sha256'] = obj_attr['ChecksumSHA256']
        return obj_info
