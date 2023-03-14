import re
from types import SimpleNamespace

from .util import validate_regexp


class NationalID:
    """
    Nepal national identity card number, NIN
    https://en.wikipedia.org/wiki/National_identification_number#Nepal
    https://nimc.gov.ng/about-nin/
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'NP',
        'min_length': 11,
        'max_length': 11,
        # length without insignificant chars
        'parsable': False,
        # has parse function
        'checksum': False,
        # has checksum function
        'regexp': re.compile(r'^\d{11}$')
        # regular expression to validate the id
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        return validate_regexp(id_number, NationalID.METADATA.regexp)


NIN = NationalID
"""
alias of https://nimc.gov.ng/about-nin/
"""
