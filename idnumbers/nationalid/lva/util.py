import re


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'-', '', id_number)


def is_new_personal_code(id_number: str) -> bool:
    """use the first 2 char to determine the new or old format"""
    try:
        return int(id_number[0:2]) > 31
    except ValueError:
        return False
