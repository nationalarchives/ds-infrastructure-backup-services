import boto3
import botocore.exceptions
from .helpers import find_value_dict, find_key_dict, calc_timedelta, extract_checksum_details


class Bucket:
    def __init__(self, region: str = 'eu-west-2'):
        self.client = boto3.client('s3',
                                   region_name=region)
        self.legal_holds = ['ON', 'OFF']
        self.lock_modes = ['GOVERNANCE', 'COMPLIANCE']
        self.storage_classes = ['STANDARD', 'STANDARD_IA', 'INTELLIGENT_TIERING', 'GLACIER', 'DEEP_ARCHIVE',
                                'GLACIER_IR']

    def get_object_info(self, *, bucket: str, key: str):
        try:
            obj_get = self.client.get_object(Bucket=bucket, Key=key, Range='bytes=0-0')
            obj_attr = self.client.get_object_attributes(Bucket=bucket, Key=key,
                                                         ObjectAttributes=['Checksum', 'StorageClass', 'ObjectSize'])
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
                    'content_length': obj_attr['ObjectSize'],
                    'etag': obj_get['ETag'].replace('"', ''),
                    'content_type': obj_get['ContentType'],
                    'serverside_encryption': obj_get['ServerSideEncryption'], }
        if "ExpiresString" in obj_get:
            obj_info['expires_string'] = obj_get['ExpiresString']
        if "VersionId" in obj_get:
            obj_info['version_id'] = obj_get['VersionId']
        else:
            obj_info['version_id'] = None
        if "Metadata" in obj_get:
            obj_info['metablock'] = obj_get['Metadata']
            if find_value_dict("storage_class", obj_get['Metadata']):
                obj_info['storage_class'] = obj_get['Metadata']['storage_class']
            if find_value_dict("expiration_period", obj_get['Metadata']):
                obj_info['expiration_period'] = obj_get['Metadata']['expiration_period']
            if find_value_dict("retention_period", obj_get['Metadata']):
                obj_info['retention_period'] = obj_get['Metadata']['retention_period']
            if find_value_dict("lock_mode", obj_get['Metadata']):
                obj_info['lock_mode'] = obj_get['Metadata']['lock_mode']
            if find_value_dict("legal_hold", obj_get['Metadata']):
                obj_info['legal_hold'] = obj_get['Metadata']['legal_hold']
        checksum = extract_checksum_details(obj_attr)
        if checksum is not None:
            obj_info['checksum_encoding'] = checksum['checksum_encoding']
            obj_info['checksum'] = checksum['checksum']
        if 'SSECustomerAlgorithm' in obj_info:
            obj_info['sse_customer_algorithm'] = obj_attr['SSECustomerAlgorithm']
        if 'SSECustomerKeyMD5' in obj_info:
            obj_info['sse_customer_key_md5'] = obj_attr['SSECustomerKeyMD5']
        if 'SSEKMSKeyId' in obj_info:
            obj_info['sse_kms_key_id'] = obj_attr['SSEKMSKeyId']
        return obj_info

    def get_object_tags(self, *, bucket: str, key: str, version_id: str = None):
        if version_id:
            response = self.client.get_object_tags(Bucket=bucket, Key=key, VersionId=version_id)
        else:
            response = self.client.get_object_tags(Bucket=bucket, Key=key)
        return response['TagSet']

    def create_multipart_upload(self, endpoint: str, object_key: str, expires: str = None,
                                metadata: dict = None, content_type: str = None,
                                storage_class: str = None, expiration_period: str = None,
                                retention_period: str = None, legal_hold: str = 'OFF',
                                lock_mode: str = None, ):
        if storage_class is None or storage_class.upper() not in self.storage_classes:
            storage_class = 'GLACIER'
        if legal_hold is None or legal_hold.upper() not in self.legal_holds:
            legal_hold = 'ON'
        if lock_mode is not None and lock_mode.upper() not in self.lock_modes:
            lock_mode = 'GOVERNANCE'
        expires = calc_timedelta(expiration_period)
        retention = calc_timedelta(retention_period)
        params = {
            'Bucket': endpoint,
            'Key': object_key,
            'Metadata': metadata,
            'ContentType': content_type,
            'StorageClass': storage_class.upper(),
            'Expires': expires,
            'ObjectLockRetainUntilDate': retention,
            'ObjectLockLegalHoldStatus': legal_hold.upper(),
            'ObjectLockMode': lock_mode.upper()
        }
        param_set = {k: v for k, v in params.items() if v is not None}
        try:
            response = self.client.create_multipart_upload(**param_set)
        except botocore.exceptions.ClientError as error:
            print(f'S3 - create part upload {error.response["Error"]["Code"]}')
            return None
        return response['UploadId']

    def upload_part_copy(self, copy_src: dict, endpoint: str, target_key: str, copy_source_range: str,
                         upload_id: str, part_number: int, ):
        try:
            response = self.client.upload_part_copy(Bucket=endpoint, Key=target_key,
                                                    CopySource=copy_src, CopySourceRange=copy_source_range,
                                                    UploadId=upload_id, PartNumber=part_number)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchUpload':
                print('S3 - part upload - NoSuchUpload')
            else:
                print('S3 - part upload - unknown error')
            print(error.response['Error']['Code'])
            return None
        return_value = {'ETag': response['CopyPartResult']['ETag'],
                        'PartNumber': part_number}
        if 'checksum_encoding' in response['CopyPartResult']:
            obj_cp_rec['checksum_encoding'] = checkin_rec['checksum_encoding']
            obj_cp_rec['checksum'] = checkin_rec['checksum']

        if find_key_dict('ChecksumCRC32', response['CopyPartResult']):
            return_value['ChecksumCRC32'] = response['CopyPartResult']['ChecksumCRC32']
        if find_key_dict('ChecksumCRC32C', response['CopyPartResult']):
            return_value['ChecksumCRC32C'] = response['CopyPartResult']['ChecksumCRC32C']
        if find_key_dict('ChecksumSHA1', response['CopyPartResult']):
            return_value['ChecksumSHA1'] = response['CopyPartResult']['ChecksumSHA1']
        if find_key_dict('ChecksumSHA256', response['CopyPartResult']):
            return_value['ChecksumSHA256'] = response['CopyPartResult']['ChecksumSHA256']
        return return_value

    def complete_multipart_upload(self, endpoint: str, target_key: str, parts: dict, upload_id: str, ):
        try:
            response = self.client.complete_multipart_upload(Bucket=endpoint, Key=target_key,
                                                             MultipartUpload=parts, UploadId=upload_id)
        except botocore.exceptions.ClientError as error:
            print(f'S3 - create part upload {error.response["Error"]["Code"]}')
            return None
        return_value = {'location': response['Location'], 'bucket': response['Bucket'],
                        'object_key': response['Key'], 'etag': response['ETag'],
                        'server_side_encryption': response['ServerSideEncryption']}
        if find_key_dict('VersionId', response):
            return_value['version_id'] = response['VersionId']
        if find_key_dict('Expiration', response):
            return_value['expiration'] = response['Expiration']
        if find_key_dict('SSEKMSKeyId', response):
            return_value['sse_kmd_key_id'] = response['SSEKMSKeyId']
        if find_key_dict('ChecksumCRC32', response):
            return_value['ChecksumCRC32'] = response['ChecksumCRC32']
        if find_key_dict('ChecksumCRC32C', response):
            return_value['ChecksumCRC32C'] = response['ChecksumCRC32C']
        if find_key_dict('ChecksumSHA1', response):
            return_value['ChecksumSHA1'] = response['ChecksumSHA1']
        if find_key_dict('ChecksumSHA256', response):
            return_value['ChecksumSHA256'] = response['ChecksumSHA256']
        return return_value

    def abort_multipart_upload(self, endpoint: str, target_key: str, upload_id: str, ):
        try:
            response = self.client.abort_multipart_upload(Bucket=endpoint, Key=target_key, UploadId=upload_id)
        except botocore.exceptions.ClientError as error:
            print(f'S3 - abort part upload - {error.response["Error"]["Code"]}')
            return None
        return response

    def copy_object(self, copy_source: dict, target_endpoint: str, target_key: str,
                    storage_class: str = None, expiration_period: str = None,
                    retention_period: str = None, legal_hold: str = 'OFF',
                    lock_mode: str = None, metadata: dict = None, content_type: str = None, ):
        if storage_class is None or storage_class.upper() not in self.storage_classes:
            storage_class = 'GLACIER'
        if legal_hold is not None:
            legal_hold = legal_hold.upper()
            if legal_hold not in self.legal_holds:
                legal_hold = 'ON'
        if lock_mode is not None:
            lock_mode = lock_mode.upper()
            if lock_mode not in self.lock_modes:
                lock_mode = 'GOVERNANCE'
        expires = calc_timedelta(expiration_period)
        retention = calc_timedelta(retention_period)
        params = {
            'CopySource': copy_source,
            'Bucket': target_endpoint,
            'Key': target_key,
            'Metadata': metadata,
            'ContentType': content_type,
            'StorageClass': storage_class.upper(),
            'Expires': expires,
            'ObjectLockRetainUntilDate': retention,
            'ObjectLockLegalHoldStatus': legal_hold,
            'ObjectLockMode': lock_mode
        }
        print(params)
        param_set = {k: v for k, v in params.items() if v is not None}
        try:
            response = self.client.copy_object(**param_set)
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
