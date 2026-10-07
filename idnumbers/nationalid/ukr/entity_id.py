import re
from ..metadata import IdMetadata
from typing import Optional
from ..util import validate_regexp


class EntityIDNumber:
    """
    The legal entity ID number in Ukraine
    https://uk.wikipedia.org/wiki/%D0%9A%D0%BE%D0%B4_%D0%84%D0%94%D0%A0%D0%9F%D0%9E%D0%A3
    https://1cinfo.com.ua/Article/Detail/Proverka_koda_po_EDRPOU/
    This is a python version of https://github.com/alazurenko/validate-edrpou
    Second-pass remainder mapping reference:
    https://github.com/arthurdejong/python-stdnum/blob/2.2/stdnum/ua/edrpou.py
    alias: ["EDRPOU", "ЄДРПОУ"]
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'UA',
        # length without insignificant chars
        'min_length': 8,
        'max_length': 8,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^\d{8}$'),
        'alias_of': None,
        'names': ['Legal Entity ID Number',
                  'EDRPOU',
                  'ЄДРПОУ'],
        'links': ['https://uk.wikipedia.org/wiki/%D0%9A%D0%BE%D0%B4_%D0%84%D0%94%D0%A0%D0%9F%D0%9E%D0%A3',
                  'https://1cinfo.com.ua/Article/Detail/Proverka_koda_po_EDRPOU/'],
        'deprecated': False,
        'country_name': 'Ukraine',
        'id_type': 'Legal Entity ID Number',
        'official_name': 'Код ЄДРПОУ',
        'display_format': '########',
        'example': '32000001',
        'checksum_algorithm': 'Weighted sum mod 11 (weights 1-7, or 7 then 1-6 when the first digit is 3 to 6; a '
                              'remainder of 10 retries with every weight raised by 2)',
        'masks': ('########',)
    })

    PHASE1_MULTIPLIER = [1, 2, 3, 4, 5, 6, 7]
    PHASE2_MULTIPLIER = [7, 1, 2, 3, 4, 5, 6]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the EDRPOU
        """
        if not validate_regexp(id_number, EntityIDNumber.METADATA.regexp):
            return False
        return EntityIDNumber.checksum(id_number) == int(id_number[7])

    @staticmethod
    def checksum(id_number: str) -> Optional[int]:
        """algorithm: https://1cinfo.com.ua/Article/Detail/Proverka_koda_po_EDRPOU/"""
        if not validate_regexp(id_number, EntityIDNumber.METADATA.regexp):
            return None
        number_list = [int(char) for char in list(id_number)]
        source_list = number_list[:7]
        if source_list[0] < 3 or source_list[0] > 6:
            multiplier = EntityIDNumber.PHASE1_MULTIPLIER
        else:
            multiplier = EntityIDNumber.PHASE2_MULTIPLIER
        modulus = sum([value * multiplier[index] for (index, value) in enumerate(source_list)]) % 11
        if modulus < 10:
            return modulus
        multiplier = [val + 2 for val in multiplier]
        # A second-pass remainder of 10 maps to check digit 0.
        modulus = sum([value * multiplier[index] for (index, value) in enumerate(source_list)]) % 11
        return modulus % 10
