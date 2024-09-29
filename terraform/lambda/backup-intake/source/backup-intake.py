import boto3
import json
import random
import string
import mysql.connector
from mysql.connector import errorcode
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    obj_data = event['Records'][0]['s3']

    result = process_object(obj_data)


def process_object(obj_data):
    bucket = obj_data['bucket']['name']
    path = obj_data['object']['key']

    retention_period = '90d'
    lock_mode = ''
    legal_hold = 'OFF'
    lock_until_date = '1900-01-01'

    print("request for " + bucket + "/" + path)

    object = path.split('/')[-1]
    object_key = "/".join(path.split('/')[:-1])

    print("bucket - " + bucket)
    print("object_key - " + object_key)
    print("object - " + object)

    s3Client = boto3.client('s3')
    print("s3Client")
    response = s3Client.get_object(Bucket=bucket, Key=path)
    print(response)
    print("intake_token - " + ''.join(random.choice(string.ascii_letters + string.digits) for i in range(64)))
    print("last_modified - " + response['ResponseMetadata']['HTTPHeaders']['last-modified'])
    print("content_length - " + str(response['ContentLength']))
    print("ETag - " + str(response['ETag']))

    if "Metadata" in response:
        obj_metadata = response['Metadata']
        if case_insensitive_key(obj_metadata, "retention_period"):
            print("retention - " + obj_metadata['retention_period'])
            retention_period = obj_metadata['retention_period']
        else:
            print("retention - standard")
        if case_insensitive_key(obj_metadata, "lockmode"):
            print("lock_mode - " + obj_metadata['lock_mode'])
            lock_mode = obj_metadata['lock_mode']
        if case_insensitive_key(obj_metadata, "legal_hold"):
            print("legal_hold - " + obj_metadata['legal_hold'])
            legal_hold = obj_metadata['legal_hold']
        if case_insensitive_key(obj_metadata, "lock-until-date"):
            print("lock_until_date - " + obj_metadata['lock-until-date'])
            lock_until_date = obj_metadata['lock-until-date']

    # get secrets
    sm_client = boto3.client('secretsmanager')
    sm_response = sm_client.get_secret_value(SecretId='/infrastructure/back-service/lambda/credentials')

    secrets = json.loads(sm_response['SecretString'])

    sql_command = "INSERT INTO s3_triggers (bucket, object_key, object_name, object_size, last_modified, retention_period, lock_mode, legal_hold, lock_until_date) VALUES ('{bucket}', '{object_key}', '{object_name}', {object_size}, '{last_modified}', '{retention_period}', '{lock_mode}', '{legal_hold}', '{lock_until_date}')".format(
        bucket=bucket, object_key=object_key, object_name=object, object_size=str(response['ContentLength']),
        last_modified=response['ResponseMetadata']['HTTPHeaders']['last-modified'], retention_period=retention_period,
        lock_mode=lock_mode, legal_hold=legal_hold, lock_until_date=lock_until_date)

    print(sql_command)

    # connect to DB
    db_config = {
        'user': secrets['db_username'],
        'password': secrets['db_password'],
        'host': secrets['db_host'],
        'database': secrets['db_name'],
        'raise_on_warnings': True
    }

    try:
        db_connect = mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        db_cursor = db_connect.cursor()

        db_cursor.execute(sql_command)
        db_connect.commit()

        event_id = db_cursor.lastrowid
        print("event-id: " + str(event_id))

        db_cursor.close()
        db_connect.close()


def case_insensitive_key(a, k):
    k = k.lower()
    return [a[key] for key in a if key.lower() == k]


def get_mysql_creds():
    secret_id = 'lambda/backup-intake/mysql'
    region = 'eu-west-2'
    client = boto3.client('secretsmanager')
    try:
        secret = client.get_secret_value(
            SecretId=secret_id,
            region_name=region
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_id + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            print("The requested secret can't be decrypted using the provided KMS key:", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            print("An error occurred on service side:", e)
        return False
    else:
        js_info = json.load(secret['SecretString'])
        return js_info


def size_converter(value=0, start='B', end='GB', precision=2, long_names=False, base=1024):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    units_long = ['Byte', 'Kilobyte', 'Megabyte', 'Gigabyte', 'Terabyte', 'Petabyte', 'Exabyte', 'Zettabyte', 'Yottabyte']
    start_index = units.index(start.upper())
    end_index = units.index(end.upper())
    if start_index == end_index:
        if start == 'B':
            output_unit = start.upper() if not long_names else ' ' + units_long[start_index]
            return '{:d}{unit}'.format(value, unit=output_unit)
        else:
            output_unit = start.upper() if not long_names else ' ' + units_long[start_index]
            return '{:.{precision}f}{unit}'.format(value, precision=precision, unit=output_unit)
    elif start_index < end_index:
        result = value / pow(base,(end_index - start_index))
        output_unit = end.upper() if not long_names else ' ' + units_long[end_index]
        return '{:.{precision}f}{unit}'.format(result, precision=precision, unit=output_unit)
    elif start_index > end_index:
        output_unit = start.upper() if not long_names else ' ' + units_long[start_index]
        result = value * pow(base, (start_index - end_index))
        return '{:.{precision}f}{unit}'.format(result, precision=precision, unit=output_unit)
    else:
        return "n/a"

