import re
from ..metadata import IdMetadata
from typing import Optional

from ..util import CHECK_DIGIT, validate_regexp, luhn_digit


class NationalID:
    """
    Israel Identity Number, מספר זהות, Mispar Zehut
    https://en.wikipedia.org/wiki/National_identification_number#Israel
    https://taxid.pro/docs/countries/israel

    The python-stdnum 2.2 algorithm requires a positive numeric value independently of the Luhn check:
    https://github.com/arthurdejong/python-stdnum/blob/2.2/stdnum/il/idnr.py
    This excludes the all-zero number; passing these checks does not establish that an ID was issued.
    """
    METADATA = IdMetadata(**{
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
        return (check_digit is not None and id_number != '000000000'
                and str(check_digit) == id_number[-1])

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """Calculate national id checksum, or None if the input does not match the format"""
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return None
        numbers = [int(i) for i in id_number]
        return luhn_digit(numbers[:-1], False)
