import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import CHECK_DIGIT, validate_regexp, weighted_modulus_digit


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[ -]', '', id_number)


class ParseResult(TypedDict):
    """The parse result of Iceland ID"""
    yyyymmdd: date
    """dob"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """check digit"""


class IcelandicID:
    """
    Iceland Icelandic identification number, kennitala
    https://en.wikipedia.org/wiki/Icelandic_identification_number
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'IS',
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<dd>\d{2})(?P<mm>\d{2})(?P<yy>\d{2})-?'
                             r'(?P<sn>\d{2})'
                             r'(?P<checksum>\d)'
                             r'(?P<century>\d)$')
    })

    WEIGHTS = [3, 2, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate"""
        if not validate_regexp(id_number, IcelandicID.METADATA.regexp):
            return False
        return IcelandicID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = IcelandicID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        checksum = IcelandicID.checksum(id_number)
        if not checksum:
            return None
        if match_obj.group('century') == '9':
            year_base = 1900
        elif match_obj.group('century') == '0':
            year_base = 2000
        else:
            return None
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        try:
            return {
                'yyyymmdd': date(yy + year_base, mm, dd),
                'sn': match_obj.group('sn'),
                'checksum': int(match_obj.group('checksum')),
            }
        except ValueError:
            # catch the date error
            return None

    @staticmethod
    def checksum(id_number) -> bool:
        """
        check the checksum
        https://en.wikipedia.org/wiki/Icelandic_identification_number
        ref: https://github.com/aldavigdis/kennitala-gem/blob/main/lib/kennitala.rb#L295 for the 10
        """
        if not validate_regexp(id_number, IcelandicID.METADATA.regexp):
            return False
        numbers = [int(char) for char in normalize(id_number)]
        modulus = weighted_modulus_digit(numbers[0:-2], IcelandicID.WEIGHTS, 11, True)
        if modulus == 10:
            # ref https://github.com/aldavigdis/kennitala-gem/blob/main/lib/kennitala.rb#L295
            return False
        modulus = 0 if modulus == 0 else 11 - modulus
        return numbers[-2] == modulus


NationalID = IcelandicID
"""alias of IcelandicID"""
