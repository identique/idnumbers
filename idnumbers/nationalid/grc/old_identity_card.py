import re
from types import SimpleNamespace
from ..util import validate_regexp


class OldIdentityCard:
    """
    Greece Identity Card, the old one.
    https://en.wikipedia.org/wiki/National_identification_number#Greece
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'GR',
        'min_length': 7,
        'max_length': 7,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]-?\d{6}$'),
        'alias_of': None,
        'names': ['Identity Card Number'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Greece'],
        'deprecated': True
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate with regexp
        """
        return validate_regexp(id_number, OldIdentityCard.METADATA.regexp)
