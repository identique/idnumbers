import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import CHECK_DIGIT, validate_regexp, luhn_digit, verhoeff_check


class ParseResult(TypedDict):
    """The parse result of Luxembourg ID"""
    yyyymmdd: date
    """dob"""
    sn: str
    """serial number"""
    checksum1: CHECK_DIGIT
    """check digit"""
    checksum2: CHECK_DIGIT
    """check digit"""


class NationalID:
    """
    Luxembourg National ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Luxembourg
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Luxembourg-TIN.pdf
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'LU',
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<yyyy>\d{4})(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum1>\d)'
                             r'(?P<checksum2>\d)$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate"""
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        checksum = NationalID.checksum(id_number)
        if not checksum:
            return None
        yyyy = int(match_obj.group('yyyy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        try:
            return {
                'yyyymmdd': date(yyyy, mm, dd),
                'sn': match_obj.group('sn'),
                'checksum1': int(match_obj.group('checksum1')),
                'checksum2': int(match_obj.group('checksum2'))
            }
        except ValueError:
            # catch the date error
            return None

    @staticmethod
    def checksum(id_number) -> bool:
        """check the checksum"""
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        numbers = [int(char) for char in id_number]
        check1 = luhn_digit(numbers[0:-2], True)
        if check1 != numbers[-2]:
            return False
        # clone the numbers and remove the 12th digit
        check2_numbers = list(numbers)
        del check2_numbers[-2]
        # perform verhoeff check
        return verhoeff_check(check2_numbers)
