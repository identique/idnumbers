import re
from types import SimpleNamespace

from .util import validate_regexp


class NationalID:
    """
    Papua New Guinea national id, NID
    https://en.wikipedia.org/wiki/National_identification_number#Moldova
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'PG',
        # length without insignificant chars
        'min_length': 10,
        'max_length': 10,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^\d{10}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NID
        """
        return validate_regexp(id_number, NationalID.METADATA.regexp)
