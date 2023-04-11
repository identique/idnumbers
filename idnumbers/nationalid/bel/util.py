import re


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return re.sub(r'[.-]', '', id_number)


def calc_check_digits(id_number: int) -> int:
    """
    calculated as the remainder of dividing xxxxxxxxxx by 97
    (if the remainder is 0, the check number is set to 97)
    """
    return 97 - id_number % 97
