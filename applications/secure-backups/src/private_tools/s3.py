import boto3
import botocore.exceptions
import re, json
from .db_mysql import Database
from datetime import datetime
from dateutil.parser import *
from .helpers import find_value_dict, find_key_dict


class Bucket:
    def __init__(self, region: str = 'eu-west-2'):
        self.client = boto3.client('s3',
                                   region_name=region)

    def get_object_info(self, *, bucket: str, key: str):
        try:
            obj_get = self.client.get_object(Bucket=bucket,
                                             Key=key)
            obj_attr = self.client.get_object_attributes(Bucket=bucket, Key=key,
                                                         ObjectAttributes=['Checksum', 'StorageClass'])
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchKey':
                print('S3 - NoSuchKey')
            elif error.response['Error']['Code'] == 'InvalidObjectState':
                print('S3 - InvalidObjectState')
            else:
                print('S3 - unknown error')
            print(error.response['Error']['Code'])
            return None
        obj_info = {'bucket_name': bucket, 'object_key': key,
                    'last_modified': obj_get['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    'content_length': obj_get['ContentLength'],
                    'etag': obj_get['ETag'].replace('"', ''),
                    'content_type': obj_get['ContentType'],
                    'serverside_encryption': obj_get['ServerSideEncryption'],
                    'storage_class': obj_attr['StorageClass']}
        if "ExpiresString" in obj_get:
            obj_info['expires_string'] = obj_get['ExpiresString']
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

    def create_multipart_upload(self, bucket: str, object_key: str, expires: str = None,
                                metadata: dict = None, content_type: str = None,
                                checksum_algorithm: str = None, ):
        params = {'Bucket': bucket, 'Key': object_key}
        if expires:
            params['Expires'] = expires
        if metadata:
            params['Metadata'] = metadata
        if content_type:
            params['ContentType'] = content_type
        if checksum_algorithm:
            params['ChecksumAlgorithm'] = checksum_algorithm
        response = self.client.create_multipart_upload(**params, )
        return response['UploadId']

    def upload_part_copy(self, copy_src: dict, bucket: str, object_key: str, copy_source_range: str,
                         upload_id: str, part_number: int, ):
        regex_set = [{'re_compile': re.compile(r'(?<![{}\[\]])\n'), 'replace_with': ',\n'},
                     {'re_compile': re.compile(r',(?=\s*?[{\[\]}])'), 'replace_with': ''}]
        response = self.client.upload_part_copy(Bucket=bucket, Key=object_key,
                                                CopySource=copy_src, CopySourceRange=copy_source_range,
                                                UploadId=upload_id, PartNumber=part_number)
        return_value = {'ETag': response['CopyPartResult']['ETag'],
                        'PartNumber': part_number}
        if find_key_dict('ChecksumCRC32', response['CopyPartResult']):
            return_value['ChecksumCRC32'] = response['CopyPartResult']['ChecksumCRC32']
        if find_key_dict('ChecksumCRC32C', response['CopyPartResult']):
            return_value['ChecksumCRC32C'] = response['CopyPartResult']['ChecksumCRC32C']
        if find_key_dict('ChecksumSHA1', response['CopyPartResult']):
            return_value['ChecksumSHA1'] = response['CopyPartResult']['ChecksumSHA1']
        if find_key_dict('ChecksumSHA256', response['CopyPartResult']):
            return_value['ChecksumSHA256'] = response['CopyPartResult']['ChecksumSHA256']
        return return_value

    def complete_multipart_upload(self, bucket: str, object_key: str, parts: dict, upload_id: str, ):
        response = self.client.complete_multipart_upload(Bucket=bucket, Key=object_key,
                                                         MultipartUpload=parts, UploadId=upload_id)
        print(response)
        return_value = {'location': response['Location'], 'bucket': response['Bucket'],
                        'object_key': response['Key'],
                        'etag': response['ETag'], 'version_id': response['VersionId'],
                        'server_side_encryption': response['ServerSideEncryption']}
        if find_key_dict('Expiration', response):
            return_value['expiration'] = response['Expiration']
        if find_key_dict('SSEKMSKeyId', response):
            return_value['sse_kmd_key_id'] = response['SSEKMSKeyId']
        if find_key_dict('ChecksumCRC32', response['CopyPartResult']):
            return_value['ChecksumCRC32'] = response['CopyPartResult']['ChecksumCRC32']
        if find_key_dict('ChecksumCRC32C', response['CopyPartResult']):
            return_value['ChecksumCRC32C'] = response['CopyPartResult']['ChecksumCRC32C']
        if find_key_dict('ChecksumSHA1', response['CopyPartResult']):
            return_value['ChecksumSHA1'] = response['CopyPartResult']['ChecksumSHA1']
        if find_key_dict('ChecksumSHA256', response['CopyPartResult']):
            return_value['ChecksumSHA256'] = response['CopyPartResult']['ChecksumSHA256']
        return return_value

    def xget_object_info(self, bucket: str, object_key: str):
        try:
            obj_data = self.client.get_object(Bucket=bucket,
                                              Key=object_key)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchKey':
                print('S3 - NoSuchKey')
                return None
            elif error.response['Error']['Code'] == 'InvalidObjectState':
                print('S3 - InvalidObjectState')
            else:
                print('S3 - unknown error')
            raise error
        else:
            return obj_data

    def xget_object_attr(self, bucket: str, object_key):
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

    def copy_object(self, source_bucket: str, source_key: str, target_bucket: str, target_key: str):
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

    def rm_object(self, bucket: str, key: str):
        response = self.client.delete_object(Bucket=bucket,
                                             Key=key)
        return response


class RBucket:
    def __init__(self, region: str = 'eu-west-2'):
        self.resource = boto3.resource('s3',
                                       region_name=region)

    def cp(self, cp_source, target_bucket, target_key, callback, locking, ):
        try:
            self.resource.meta.client.copy(CopySource=cp_source, Bucket=target_bucket, Key=target_key,
                                           Callback=callback)
        except Exception as e:
            raise e
        if locking:
            self.set_locking(locking, target_bucket, target_key)

    def set_locking(self, info, target_bucket, target_key):
        vdate = find_value_dict("retain_until_date", info)
        vmode = find_value_dict("lock_mode", info)
        vhold = find_value_dict("legal_hold", info)
        try:
            until_date = parse(vdate)
        except:
            pass
        else:
            if vdate and vmode:
                response = self.resource.put_object_retention(Bucket=target_bucket, Key=target_key,
                                                              Retention={'Mode': vmode,
                                                                         'retain_until_date': vdate})
        if vhold:
            if vhold.upper() == 'ON' or vhold.upper() == 'OFF':
                response = self.resource.put_object_legal_hold(Bucket=target_bucket, Key=target_key,
                                                               LegalHold={'Status': vhold.upper()})


class S3CopyProgress:
    def __init__(self, object_summary, db_secrets_vals):
        self.object_summary = object_summary
        self.db_secrets_vals = db_secrets_vals
        self.bytes_transferred_total = 0

    def update_progress(self, bytes_transferred):
        db_connect = Database(self.db_secrets_vals)
        self.bytes_transferred_total += bytes_transferred
        percent_complete = round((self.bytes_transferred_total / self.object_summary['size']) * 100)
        cp_rec = {'updated_at': str(datetime.now())[0:19], 'percentage': str(percent_complete)}
        db_connect.update('object_copies', cp_rec)
        db_connect.where(f'id = {self.object_summary["id"]}')
        db_connect.run()
        db_connect.close()
        print(f'[{self.object_summary["key"]}] {percent_complete}% of {self.object_summary["size"]}')


class s3_object:
    def __init__(self, *, region: str):
        self.client = boto3.client('s3',
                                   region_name=region)

    def info(self, *, bucket: str, key: str):
        try:
            obj_get = self.client.get_object(Bucket=bucket,
                                             Key=key)
            obj_attr = self.client.get_object_attributes(Bucket=bucket,
                                                         Key=key,
                                                         VersionId=obj_get['VersionId'],
                                                         ObjectAttributes=['Checksum',
                                                                           'StorageClass'])
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchKey':
                print('S3 - NoSuchKey')
            elif error.response['Error']['Code'] == 'InvalidObjectState':
                print('S3 - InvalidObjectState')
            else:
                print('S3 - unknown error')
            raise error
        obj_info = {'bucket_name': bucket, 'object_key': key,
                    'last_modified': obj_get['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    'content_length': obj_get['ContentLength'],
                    'expires_string': obj_get['ExpiresString'],
                    'etag': obj_get['ETag'].replace('"', ''),
                    'version_id': obj_get['VersionId'],
                    'content_type': obj_get['ContentType'],
                    'serverside_encryption': obj_get['ServerSideEncryption'],
                    'storage_class': obj_attr['StorageClass']}
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
