import re
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import CHECK_DIGIT, luhn_digit, validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[ \-/]', '', id_number)


class ParseResult(TypedDict):
    """Parse result of EmiratesID"""
    yyyy: int
    """year of birth"""
    sn: int
    """serial number"""
    checksum: CHECK_DIGIT
    """check digits"""


class EmiratesIDNumber:
    """
    ARE Emirates/Resident ID number format
    https://en.wikipedia.org/wiki/National_identification_number#United_Arab_Emirates
    This is the python version of https://gist.github.com/geordee/e51d111426de675c0c0f8503c2003047
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AE',
        'min_length': 15,
        'max_length': 15,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^784[ -]?'
                             r'(?P<yyyy>\d{4})[ -]?'
                             r'(?P<sn>\d{7})[ -]?'
                             r'(?P<checksum>\d)$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the ARE id number
        """
        if not id_number:
            return False

        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return EmiratesIDNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = EmiratesIDNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        yyyy = match_obj.group('yyyy')
        sn = match_obj.group('sn')
        checksum_str = match_obj.group('checksum')
        checksum = EmiratesIDNumber.checksum(id_number)
        if checksum is None or str(checksum) != checksum_str:
            return None
        else:
            return {
                'yyyy': int(yyyy),
                'sn': sn,
                'checksum': checksum
            }

    @staticmethod
    def checksum(id_number) -> Optional[CHECK_DIGIT]:
        """use luhn algorithm to calculate the check digit"""
        if not validate_regexp(id_number, EmiratesIDNumber.METADATA.regexp):
            return None
        normalized = normalize(id_number)
        return luhn_digit([int(char) for char in normalized[:-1]])


NationalID = EmiratesIDNumber
"""alias of EmiratesIDNumber"""
