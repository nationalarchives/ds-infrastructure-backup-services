import random
import string
import re
import boto3
import botocore.exceptions
import json

from setuptools.command.upload import upload


def size_converter(value: int=0, start: str='B', end: str='GB', precision: int=2, long_names: bool=False, base: int=1024):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    units_long = ['Byte', 'Kilobyte', 'Megabyte', 'Gigabyte', 'Terabyte', 'Petabyte', 'Exabyte', 'Zettabyte',
                  'Yottabyte']
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
        result = value / pow(base, (end_index - start_index))
        output_unit = end.upper() if not long_names else ' ' + units_long[end_index]
        return '{:.{precision}f}{unit}'.format(result, precision=precision, unit=output_unit)
    elif start_index > end_index:
        output_unit = start.upper() if not long_names else ' ' + units_long[start_index]
        result = value * pow(base, (start_index - end_index))
        return '{:.{precision}f}{unit}'.format(result, precision=precision, unit=output_unit)
    else:
        return "n/a"


def set_random_id(length: int = 64):
    random.seed()
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


def find_key_dict(k: str, a: dict = {}):
    k = k.casefold()
    return [key for key in a if key.casefold() == k]


def find_value_dict(k: str, a: dict = {}):
    k = k.casefold()
    return [a[key] for key in a if key.casefold() == k]


def sub_json(text: str, re_set):
    prepared_dict = text
    for step in re_set:
        prepared_dict = re.sub(step['re_compile'], step['replace_with'], prepared_dict)
    return prepared_dict


def deconstruct_path(object_key):
    if object_key.startswith('/'):
        object_key = object_key[1:]
    path_elements = object_key.split('/')
    object_name = path_elements[-1]
    if len(path_elements) > 1:
        ap_name = path_elements[0]
        location = "/".join(path_elements[:-1])
    else:
        ap_name = ''
        location = ''
    return {'object_key': object_key, 'object_name': object_name,
            'access_point': ap_name, 'location': location}


def get_parameters(name: str, aws_region: str):
    params = {}
    regex_line = re.compile(r'(?<![{}\[\]])\n')
    regex_comma = re.compile(r',(?=\s*?[{\[\]}])')
    regex_set = [{'re_compile': regex_line, 'replace_with': ',\n'},
                 {'re_compile': regex_comma, 'replace_with': ''}]
    client = boto3.client('ssm',
                          region_name=aws_region)
    try:
        response = client.get_parameter(Name=name)
    except botocore.exceptions.ClientError as error:
        raise error
    # why twice json.loads????? Is this modern python?
    values = json.loads(json.loads(sub_json(json.dumps(response['Parameter']['Value']), regex_set)))
    for k, v in values.items():
        params.update({k: v})
    return params


def create_upload_map(total_size: int, max_block_size: int=104857600):
    upload_map = []
    part_count = -(-total_size // max_block_size)
    if part_count <= 1:
        upload_map = [[0, (total_size - 1)]]
    else:
        part_size = -(-total_size // part_count)
        to_transfer_total = total_size
        for i in range(part_count):
            if i > 0:
                if upload_map[i-1][2] < part_size:
                    transfer_size = upload_map[i-1][2]
                else:
                    transfer_size = part_size
                range_from = upload_map[i-1][1] + 1
                range_to = range_from + transfer_size - 1
                to_transfer_total -= transfer_size
            else:
                range_from = 0
                range_to = part_size - 1
                to_transfer_total = total_size - part_size
            upload_map.append([range_from, range_to, to_transfer_total])
    return upload_map
