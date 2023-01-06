import re
from types import SimpleNamespace
from .util import validate_regexp


def normalize(id_number):
    return re.sub(r'[\-/]|[./]', '', id_number)


class NationalID:
    """
    CHL national ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Canada
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'CL',
        # length without insignificant chars
        'min_length': 8,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{1,2}[.]\d{3}[.]\d{3}-[\d|K])$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the CHL id number
        https://codepen.io/alisteroz/pen/KEoqgQ
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.checksum(id_number)

    MAGIC_MULTIPLIER = [3, 2, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        https://gist.github.com/ryangreenberg/4531891
        """
        normalized = normalize(id_number)
        number_list = [int(char) for char in list(normalized[:-1])]
        total = sum([value * NationalID.MAGIC_MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        checksum = 0 if (11 - total % 11) == 11 else 'K' if (11 - total % 11) == 10 else (11 - total % 11)
        check_digit = normalized[-1]
        return str(checksum) == check_digit
