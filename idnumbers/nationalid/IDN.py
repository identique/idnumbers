import re
from datetime import datetime
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import validate_regexp
from .constant import Gender
from .constant_IDN import AREA


class ParseResult(TypedDict):
    gender: Gender
    yy: str
    mm: str
    dd: str
    district: str


class NationalID:
    """
    Indonesia ID number format
    NIK (Nomor Induk Kependudukan)
    https://en.wikipedia.org/wiki/National_identification_number#Indonesia
    https://www.npmjs.com/package/nik-validator?activeTab=explore
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'IDN',
        'min_length': 16,
        'max_length': 16,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<district>\d{6})'
                             r'(?P<dd>[0-7]\d)'
                             r'(?P<mm>(0[1-9]|1[012]))'
                             r'(?P<yy>\d{2})'
                             r'(?!0000)\d{4}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the IDN id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        if not NationalID.parse(id_number):
            return False
        return True

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None

        district = AREA["kecamatan"].get(match_obj.group("district"))
        if not district:
            return None

        gender = Gender.FEMALE if int(match_obj.group('dd')[0]) <= 3 else Gender.MALE
        yy = match_obj.group('yy')
        mm = match_obj.group('mm')
        dd = match_obj.group('dd') if gender == Gender.FEMALE else int(match_obj.group('dd')) - 30

        # Validate the date
        try:
            datetime(int(f'20{yy}'), int(mm), int(dd))
            datetime(int(f'19{yy}'), int(mm), int(dd))
        except ValueError:
            return None

        return {
            "gender": gender,
            'yy': yy,
            'mm': mm,
            'dd': str(dd),
            "district": district,
        }
