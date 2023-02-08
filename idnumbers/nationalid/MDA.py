import re
from types import SimpleNamespace

from .util import validate_regexp


class PersonalCode:
    """
    Moldova Personal Code, IDNP
    https://en.wikipedia.org/wiki/National_identification_number#Moldova
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'MD',
        # length without insignificant chars
        'min_length': 13,
        'max_length': 13,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^\d{13}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the personal code
        """
        return validate_regexp(id_number, PersonalCode.METADATA.regexp)


NationalID = PersonalCode
"""alias of PersonalCode"""
