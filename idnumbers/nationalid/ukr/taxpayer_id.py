import re
from datetime import date, timedelta
from types import SimpleNamespace
from typing import List, Optional, TypedDict
from ..constant import Gender
from ..util import validate_regexp


class TaxpayerIDParseResult(TypedDict):
    """parse result of the taxpayer id"""
    yyyymmdd: date
    gender: Gender
    checksum: int


class TaxpayerIDNumber:
    """
    Ukraine Taxpayer ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Ukraine
    This is a python version of https://github.com/therezor/ua-tax-number/blob/main/src/Decoder.php
    The alias: ['RNTRC', 'РНОКПП', 'taxpayer registration number']
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'UA',
        # length without insignificant chars
        'min_length': 10,
        'max_length': 10,
        # has parse function
        'parsable': True,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^\d{10}$'),
        'alias_of': None,
        'names': ['Taxpayer ID Number',
                  'RNTRC',
                  'РНОКПП',
                  'taxpayer registration number'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Ukraine'],
        'deprecated': False
    })

    MAGIC_MULTIPLIER: List[int] = [-1, 5, 7, 9, 4, 6, 10, 5, 7]
    """multiplier for the checksum"""
    BIRTHDAY_BASE: date = date(1900, 1, 1)

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the id number
        """
        if not validate_regexp(id_number, TaxpayerIDNumber.METADATA.regexp):
            return False

        return TaxpayerIDNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[TaxpayerIDParseResult]:
        """parse the result"""
        if TaxpayerIDNumber.checksum(id_number) != int(id_number[9]):
            return None
        # according to the PHP implementation, we need to minus 1, maybe the tail and head values included.
        days = int(id_number[:5]) - 1
        dob = TaxpayerIDNumber.BIRTHDAY_BASE + timedelta(days=days)
        return {
            'yyyymmdd': dob,
            'gender': Gender.MALE if int(id_number[8]) % 2 == 1 else Gender.FEMALE,
            'checksum': int(id_number[9])
        }

    @staticmethod
    def checksum(id_number: str) -> Optional[int]:
        """algorithm: https://github.com/therezor/ua-tax-number/blob/main/src/Decoder.php"""
        if not validate_regexp(id_number, TaxpayerIDNumber.METADATA.regexp):
            return None
        number_list = [int(char) for char in list(id_number)]
        source_list = number_list[:9]
        total = sum([value * TaxpayerIDNumber.MAGIC_MULTIPLIER[index] for (index, value) in enumerate(source_list)])
        # calculate the modulus, if the value is 10, use the 0. Will it collide?
        return total % 11 % 10
