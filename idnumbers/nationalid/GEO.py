import re
from types import SimpleNamespace
from .util import validate_regexp


class PersonalNumber:
    """
    Georgia personal number format
    https://en.wikipedia.org/wiki/National_identification_number#Georgia
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'GE',
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^\d{9}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate personal number
        """
        return validate_regexp(id_number, PersonalNumber.METADATA.regexp)
