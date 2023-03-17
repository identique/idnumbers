import re
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import CHECK_DIGIT


class ParseResult(TypedDict):
    yymm: str
    """birthday of this ID"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """checksum"""


class PersonalNumber:
    """
    Bahrain Personal Number, Identification Card Number, Arabic:  الرقم الشخصي
    https://en.wikipedia.org/wiki/National_identification_number#Bahrain
    * According to the doc, we can know it has checksum algorithm. But we cannot find it.
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BH',
        'min_length': 9,
        'max_length': 9,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<yymm>\d{2}(?:0[1-9]|1[012]))'
                             r'(?P<sn>\d{4})'
                             r'(?P<checksum>\d)$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the civil number
        """
        if not id_number:
            return False

        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return PersonalNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """
        parse the id number
        """
        match_obj = PersonalNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None

        # TODO: find and implement checksum
        return {
            'yymm': match_obj.group('yymm'),
            'sn': match_obj.group('sn'),
            'checksum': int(match_obj.group('checksum'))
        }


NationalID = PersonalNumber
"""alias of PersonalNumber"""
