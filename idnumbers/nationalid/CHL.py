import re
from types import SimpleNamespace
from typing import Optional, TypedDict


def normalize(id_number):
    return re.sub(r'[\-/]|[./]', '', id_number)


class ParseResult(TypedDict):
    first_section: str
    second_section: str
    third_section: str
    check_digit: str


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
        'parsable': True,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(?P<first_section>(\d{2}|\d))'
                             r'(\.)'
                             r'(?P<second_section>\d{3})'
                             r'(\.)'
                             r'(?P<third_section>\d{3})'
                             r'(-)'
                             r'(?P<check_digit>[0-9K])$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the CHL id number
        https://codepen.io/alisteroz/pen/KEoqgQ
        """
        if not isinstance(id_number, str):
            id_number = repr(id_number)
        elif NationalID.parse(id_number) is None:
            return False
        return NationalID.checksum(id_number)

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        return {k: match_obj.group(k) for k in ['first_section', 'second_section', 'third_section', 'check_digit']}

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
