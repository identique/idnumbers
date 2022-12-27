import re
from types import SimpleNamespace

from .util import validate_regexp


class NationalID:
    """
    Japan national ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Japan
    https://tin-check.com/en/
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
        'regexp': re.compile(r"^(\d{12}$)")
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate JPN id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        https://github.com/kufu/tsubaki/blob/433d65aac341bcd58e7d8141f3f4ac374977617f/lib/tsubaki/my_number.rb#L12
        """
        arr = list(reversed((id_number[:11])))
        rem = sum([int(value) * (index + 2 if index <= 5 else (index - 4)) for (index, value) in enumerate(arr)]) % 11
        calculate_check_digit = 0 if rem <= 1 else (11 - rem)
        return int(calculate_check_digit) == int(id_number[-1])
