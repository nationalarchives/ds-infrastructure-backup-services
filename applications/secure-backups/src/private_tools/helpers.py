import random
import string
import re


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


def set_random_id(length: int = 64):
    random.seed()
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


def find_key_dict(k: str, a: dict = {}):
    k = k.lower()
    return [a[key] for key in a if key.lower() == k]

def sub_json(text: str, re_set):
    prepared_dict = text
    for step in re_set:
        prepared_dict = re.sub(step['re_compile'], step['replace_with'], prepared_dict)
    return prepared_dict

def deconstruct_path(object_key):
    return {'object_key': object_key, 'object_name': object_key.split('/')[-1],
            'location': "/".join(object_key.split('/')[:-1])}
