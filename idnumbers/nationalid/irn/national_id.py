import re
from ..metadata import IdMetadata
from typing import Optional, cast
from ..util import CHECK_DIGIT, validate_regexp, weighted_modulus_digit


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return id_number.replace('-', '')


class NationalID:
    """
    Iran national id number, (کارت ملی/kart-e-meli)
    https://en.wikipedia.org/wiki/National_identification_number#Iran,_Islamic_Republic_of

    Repeated-digit codes are rejected, following the Persian Tools validator rule:
    https://persian-tools.js.org/functions/verifyIranianNationalId.html
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'IR',
        'min_length': 10,
        'max_length': 10,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^\d{3}-?\d{6}-?\d$'),
        'alias_of': None,
        'names': ['National ID Number',
                  'kart-e-meli',
                  'کارت ملی',
                  'شماره ملی',
                  'کد ملی'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Iran,_Islamic_Republic_of',
                  'https://www.ekhtebar.ir/%E2%80%8C%D9%82%D8%A7%D9%86%D9%88%D9%86-%D8%A7%D9%84%D8%B2%D8%A7%D9%85-'
                  '%D8%A7%D8%AE%D8%AA%D8%B5%D8%A7%D8%B5-%D8%B4%D9%85%D8%A7%D8%B1%D9%87-%D9%85%D9%84%DB%8C-%D9%88-'
                  '%DA%A9%D8%AF-%D9%BE%D8%B3%D8%AA/'],
        'deprecated': False,
        'country_name': 'Iran',
        'id_type': 'National ID Number',
        'official_name': 'شماره ملی',
        'display_format': '###-######-#',
        'example': '001-234567-9',
        'checksum_algorithm': 'Weighted sum mod 11 (weights 10-2; a remainder below 2 is the check digit, otherwise 11 '
                              '- remainder)',
        'masks': ('###-######-#', '##########')
    })

    MULTIPLIER = [10, 9, 8, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        normalized = normalize(id_number)
        if len(set(normalized)) == 1:
            return False
        return NationalID.checksum(id_number) == int(id_number[-1])

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """algorithm: https://github.com/mohammadv184/idvalidator/blob/main/validate/nationalid/nationalid.go"""
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return None
        normalized = normalize(id_number)
        numbers = [int(i) for i in normalized]
        modulus = weighted_modulus_digit(numbers[:-1], NationalID.MULTIPLIER, 11, True)
        return cast(CHECK_DIGIT, modulus if modulus < 2 else 11 - modulus)
