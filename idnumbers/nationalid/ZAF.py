import re
from datetime import date
from typing import Optional, TypedDict
from types import SimpleNamespace
from .constant import Citizenship, Gender


"""
Nigeria National ID number format
https://en.wikipedia.org/wiki/National_identification_number#South_Africa
https://www.westerncape.gov.za/general-publication/decoding-your-south-african-id-number-0
"""
METADATA = SimpleNamespace(**{
    'iso3166_alpha2': 'ZA',
    'min_length': 13,
    'max_length': 13,
    'parsable': True,
    'regexp': re.compile(r'^(?P<yy>\d{2})(?P<mm>0[1-9]|1[12])'
                         r'(?P<dd>0[1-9]|[12][0-9]|3[01])'
                         r'(?P<sn>\d{4})'
                         r'(?P<citizenship>[01])(8|9)'
                         r'(?P<checksum>\d)$')
})


class ParseResult(TypedDict):
    yyyymmdd: date
    sn: str
    gender: Gender
    citizenship: Citizenship
    checksum: int


def validate(id_number: str) -> bool:
    """
    Validate the ZAF id number
    """
    if not isinstance(id_number, str):
        id_number = repr(id_number)
    return parse(id_number) is not None


def parse(id_number: str) -> Optional[ParseResult]:
    match_obj = METADATA.regexp.match(id_number)
    if not match_obj:
        return None
    elif checksum(id_number) != int(id_number[-1:]):
        return None
    else:
        year = int(match_obj.group('yy'))
        year += 2000 if year < 50 else 1900
        return {
            'yyyymmdd': date(year, int(match_obj.group('mm')), int(match_obj.group('dd'))),
            'sn': match_obj.group('sn'),
            'gender': Gender.MALE if int(match_obj.group('sn')[0]) > 4 else Gender.FEMALE,
            'citizenship': Citizenship.CITIZEN if match_obj.group('citizenship') == '0' else Citizenship.RESIDENT,
            'checksum': int(id_number[-1:])
        }


def checksum(id_number: str) -> int:
    """
    implement the algorithm of Luhn.
    https://en.wikipedia.org/wiki/Luhn_algorithm
    :param id_number:str ZAF national id
    :return: checksum number
    """
    digits = id_number[:-1]
    total_sum = 0
    for idx, char in enumerate(list(digits)):
        int_val = int(char)
        if idx % 2 == 0:
            total_sum += int_val
        elif int_val > 4:
            total_sum += (2 * int_val - 9)
        else:
            total_sum += (2 * int_val)
    return 10 - total_sum % 10
