import re
from types import SimpleNamespace
from typing import Optional

from ..util import CHECK_DIGIT, validate_regexp
from .util import normalize


class PersonalCode:
    """
    Latvia Personal Code format, personas kods
    https://en.wikipedia.org/wiki/National_identification_number#Latvia
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Latvia-TIN.pdf
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'LV',
        # length without insignificant chars
        'min_length': 11,
        'max_length': 11,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{6}-?\d{5}$)'),
        'alias_of': None,
        'names': ['Personal Code',
                  'personas kods'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Latvia',
                  'https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/Latvia-TIN.pdf'],
        'deprecated': False
    })

    MULTIPLIER = [1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    """multiplier for checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        return str(PersonalCode.checksum(id_number)) == id_number[-1]

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        if not validate_regexp(id_number, PersonalCode.METADATA.regexp):
            return None
        """Calculate national id checksum: (1101-sum) mod 11 and mod 10"""
        numbers = [int(i) for i in normalize(id_number)[:10]]
        weighted_value = sum([value * PersonalCode.MULTIPLIER[index] for (index, value) in enumerate(numbers)])
        return (1101 - weighted_value) % 11 % 10
