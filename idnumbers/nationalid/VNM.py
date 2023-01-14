import re
from math import floor
from types import SimpleNamespace
from typing import Optional, TypedDict
from .constant import Gender


def normalize(id_number: str) -> str:
    """make all characters to upper case"""
    return id_number.upper() if id_number else None


class ParseResult(TypedDict):
    """parse result for NationalID"""
    province_country_code: str
    """registration province/country code"""
    yyyy: int
    """year of birthday"""
    sn: str
    """serial number"""
    gender: Gender
    """gender, possible value: male, female"""


class NationalID:
    """
    Vietnam ID card
    https://vietnaminsider.vn/what-do-the-12-digits-on-the-citizen-id-card-with-chip-mean/
    https://lawnet.vn/en/vb/Circular-07-2016-TT-BCA-detailing-Law-on-Citizen-Identification-137-2015-ND-CP-5CCC3.html
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'VN',
        'min_length': 12,
        'max_length': 12,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<province_country_code>\d{3})'
                             r'(?P<gender>\d)'
                             r'(?P<yy>\d{2})'
                             r'(?P<sn>\d{6})$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the VNM id number
        """
        if not id_number:
            return False

        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        province_country_code = match_obj.group('province_country_code')
        century_gender = match_obj.group('gender')
        yy = match_obj.group('yy')
        sn = match_obj.group('sn')
        yyyy = NationalID.get_birth_year(int(century_gender), int(yy))
        return {
            'province_country_code': province_country_code,
            'yyyy': yyyy,
            'sn': sn,
            'gender': Gender.MALE if int(century_gender) % 2 == 0 else Gender.FEMALE
        }

    @staticmethod
    def get_birth_year(century_gender: int, yy: int) -> int:
        return 1900 + 100 * floor(century_gender / 2) + yy
