import re
from types import SimpleNamespace
from typing import Optional

from ..util import CHECK_DIGIT, validate_regexp, luhn_digit


class NationalID:
    """
    Israel Identity Number, מספר זהות, Mispar Zehut
    https://en.wikipedia.org/wiki/National_identification_number#Israel
    https://taxid.pro/docs/countries/israel
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'IL',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{9})$'),
        'alias_of': None,
        'names': ['Identity Number',
                  'מספר זהות',
                  'Mispar Zehut'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Israel',
                  'https://taxid.pro/docs/countries/israel'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        check_digit = NationalID.checksum(id_number)
        # checksum() is None unless the input is a str that matches the regexp, so [-1] is safe below
        return check_digit is not None and str(check_digit) == id_number[-1]

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return None
        """Calculate national id checksum"""
        numbers = [int(i) for i in id_number]
        return luhn_digit(numbers[:-1], False)
