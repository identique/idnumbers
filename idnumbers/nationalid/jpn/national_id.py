import re
from ..metadata import IdMetadata
from typing import Optional

from ..util import validate_regexp, weighted_modulus_digit


class MyNumber:
    """
    Japan my number format
    https://en.wikipedia.org/wiki/National_identification_number#Japan
    https://tin-check.com/en/
    https://github.com/kufu/tsubaki/blob/433d65aac341bcd58e7d8141f3f4ac374977617f/lib/tsubaki/my_number.rb#L12
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'JP',
        # length without insignificant chars
        'min_length': 12,
        'max_length': 12,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{12}$)'),
        'alias_of': None,
        'names': ['National ID Number',
                  'My Number',
                  'マイナンバー'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Japan'],
        'deprecated': False,
        'country_name': 'Japan',
        'id_type': 'My Number',
        'official_name': 'マイナンバー',
        'display_format': '############',
        'example': '765895492872',
        'checksum_algorithm': 'Weighted sum mod 11 (weights 6, 5, 4, 3, 2, 7, 6, 5, 4, 3, 2; a remainder of 0 or 1 '
                              'gives 0, otherwise 11 - remainder)',
        'masks': ('############',)
    })

    MULTIPLIER = [6, 5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    """multiplier for checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate JPN national id number
        """
        if not validate_regexp(id_number, MyNumber.METADATA.regexp):
            return False
        return MyNumber.checksum(id_number) == id_number[-1]

    @staticmethod
    def checksum(id_number: str) -> Optional[str]:
        """Calculate Japan national id checksum, None when the input is not a well-formed id number"""
        if not validate_regexp(id_number, MyNumber.METADATA.regexp):
            return None
        arr = [int(i) for i in id_number[:11]]
        rem = weighted_modulus_digit(arr, MyNumber.MULTIPLIER, 11, True)
        return str(0 if rem <= 1 else (11 - rem))
