import re
from datetime import date, timedelta
from ..metadata import IdMetadata
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
    METADATA = IdMetadata(**{
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
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Ukraine',
                  'https://uk.wikipedia.org/wiki/%D0%A0%D0%B5%D1%94%D1%81%D1%82%D1%80%D0%B0%D1%86%D1%96%D0%B9%D0%BD%D0%B8%D0%B9_%D0%BD%D0%BE%D0%BC%D0%B5%D1%80_%D0%BE%D0%B1%D0%BB%D1%96%D0%BA%D0%BE%D0%B2%D0%BE%D1%97_%D0%BA%D0%B0%D1%80%D1%82%D0%BA%D0%B8_%D0%BF%D0%BB%D0%B0%D1%82%D0%BD%D0%B8%D0%BA%D0%B0_%D0%BF%D0%BE%D0%B4%D0%B0%D1%82%D0%BA%D1%96%D0%B2'],
        'deprecated': False,
        'country_name': 'Ukraine',
        'id_type': 'Taxpayer ID Number',
        'official_name': 'Реєстраційний номер облікової картки платника податків',
        'display_format': 'DDDDDSSSSC',
        'example': '3245506789',
        'checksum_algorithm': 'Weighted sum mod 11 (weights -1, 5, 7, 9, 4, 6, 10, 5, 7; a remainder of 10 becomes 0)',
        'masks': ('##########',)
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
        if not validate_regexp(id_number, TaxpayerIDNumber.METADATA.regexp):
            return None
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
