import boto3
import json
import hashlib
from pathlib import Path

def get_asm_parameter(name: str):
    asm_client = boto3.client("secretsmanager", region_name="eu-west-2")
    secrets = asm_client.get_secret_value(SecretId=name)
    return secrets["SecretString"]


def sha256sum(filename: str) -> str:
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()


def sha1sum(filename: str) -> str:
    h = hashlib.sha1()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()


def rmdir(directory: str) -> None:
    directory = Path(directory)
    for item in directory.iterdir():
        if item.is_dir():
            directory.rmdir(item)
        else:
            item.unlink()
    directory.rmdir()


def s3_folder_exists(s3_client, bucket: str, path: str) -> bool:
    path = path.rstrip('/')
    resp = s3_client.list_objects(Bucket=bucket, Prefix=path, Delimiter='/', MaxKeys=1)
    return 'CommonPrefixes' in resp
