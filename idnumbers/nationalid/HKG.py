import re
from types import SimpleNamespace

from .util import validate_regexp


class NationalID:
    """
    Hong Kong national ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Hong_Kong
    https://pinkylam.me/playground/hkid/
    https://github.com/hsyuen720/hkid-tools/blob/main/app/utils/validate.ts
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'HK',
        # length without insignificant chars
        'min_length': 8,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r"^[A-Z]{1,2}[0-9]{6}[0-9A]$")
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate HKG id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.checksum(id_number) == id_number[-1]

    @staticmethod
    def checksum(id_number: str) -> str:
        """
        Calculate HKG national id checksum digit
        """
        arr = list(id_number[:-1])
        MULTIPLIER = [len(arr) + 1 - index for (index, _) in enumerate(arr)]
        total = 0 if len(arr) % 2 == 0 else 36 * 9
        total += sum([NationalID.get_number(arr[idx]) * mul for (idx, mul) in enumerate(MULTIPLIER)])
        rem = total % 11
        return "A" if rem == 1 else '0' if rem == 0 else str(11 - rem)

    @staticmethod
    def get_number(digit: str) -> int:
        """Convert letter to number"""
        if re.match('[A-Z]', digit):
            return int(ord(digit)) - 55
        else:
            return int(digit)
