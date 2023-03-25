import re


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[ \-/]', '', id_number)
