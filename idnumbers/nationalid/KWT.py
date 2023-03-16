import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import CHECK_DIGIT, weighted_modulus_digit, validate_regexp


class ParseResult(TypedDict):
    yyyymmdd: date
    """birthday of this ID"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """checksum"""


class CivilNumber:
    """
    Kuwait Civil Number, Arabic: الرقم المدني
    https://en.wikipedia.org/wiki/National_identification_number#Kuwait
    https://prakhar.me/articles/kuwait-civil-id-checksum/
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'KW',
        'min_length': 12,
        'max_length': 12,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<century>\d)'
                             r'(?P<yy>\d{2})'
                             r'(?P<mm>\d{2})'
                             r'(?P<dd>\d{2})'
                             r'(?P<sn>\d{4})'
                             r'(?P<checksum>\d)$')
    })

    MULTIPLIER = [2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the civil number
        """
        if not id_number:
            return False

        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return CivilNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """
        parse the id number
        """
        match_obj = CivilNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None

        checksum = CivilNumber.checksum(id_number)
        if checksum is None or str(checksum) != match_obj.group('checksum'):
            return None

        century = match_obj.group('century')
        if century == '2':
            year_base = 1900
        elif century == '3':
            year_base = 2000
        else:
            return None
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        return {
            'yyyymmdd': date(year_base + yy, mm, dd),
            'sn': match_obj.group('sn'),
            'checksum': checksum
        }

    @staticmethod
    def checksum(id_number) -> Optional[CHECK_DIGIT]:
        """
        https://prakhar.me/articles/kuwait-civil-id-checksum/
        """
        if not validate_regexp(id_number, CivilNumber.METADATA.regexp):
            return None

        numbers = [int(char) for char in id_number]
        modulus = weighted_modulus_digit(numbers[:-1], CivilNumber.MULTIPLIER, 11)
        if modulus > 10:
            # according to the algorithm, it will not be greater than 10
            return None
        return modulus


NationalID = CivilNumber
"""alias of CivilNumber"""
