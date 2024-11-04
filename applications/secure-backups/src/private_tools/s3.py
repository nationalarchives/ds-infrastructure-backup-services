import boto3
import botocore.exceptions
from .db_mysql import Database
from datetime import datetime
from .helpers import find_key_dict

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
                return None
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
    def __init__(self, region: str='eu-west-2'):
        self.resource = boto3.resource('s3',
                                   region_name=region)

    def cp(self, cp_source, target_bucket, target_key, callback, locking, ):
        try:
            self.resource.meta.client.copy(CopySource=cp_source, Bucket=target_bucket, Key=target_key, Callback=callback)
        except Exception as e:
            raise e
        if not locking:
            self.set_locking(locking, target_bucket, target_key)

    def set_locking(self, info, target_bucket, target_key):
        if find_key_dict("retain_until_date", info) and find_key_dict("lock_mode", info):
            response = self.resource.put_object_retention(Bucket=target_bucket, Key=target_key,
                                     Retention={'Mode': info['lock_mode'],
                                                'retain_until_date': info['retain_until_date']})
        if find_key_dict("legal_hold", info):
            response = self.resource.put_object_legal_hold(Bucket=target_bucket, Key=target_key,
                                                           LegalHold={'Status': 'ON'})

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
