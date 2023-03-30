import re
from types import SimpleNamespace

from ..util import validate_regexp, weighted_modulus_digit


class MyNumber:
    """
    Japan my number format
    https://en.wikipedia.org/wiki/National_identification_number#Japan
    https://tin-check.com/en/
    https://github.com/kufu/tsubaki/blob/433d65aac341bcd58e7d8141f3f4ac374977617f/lib/tsubaki/my_number.rb#L12
    """
    METADATA = SimpleNamespace(**{
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
        'deprecated': False
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
    def checksum(id_number: str) -> str:
        """Calculate Japan national id checksum"""
        arr = [int(i) for i in id_number[:11]]
        rem = weighted_modulus_digit(arr, MyNumber.MULTIPLIER, 11, True)
        return str(0 if rem <= 1 else (11 - rem))
