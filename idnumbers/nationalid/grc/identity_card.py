import re
from types import SimpleNamespace
from ..util import validate_regexp


class IdentityCard:
    """
    Greece Identity Card, the new one.
    https://en.wikipedia.org/wiki/National_identification_number#Greece
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'GR',
        'min_length': 7,
        'max_length': 7,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩABEZHIKMNOPTYX]{2}-?\d{6}$'),
        # They are two different char set, the former is Greek alphabet, the latter is Latin alphabet
        'alias_of': None,
        'names': ['Identity Card Number'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Greece'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate with regexp
        """
        return validate_regexp(id_number, IdentityCard.METADATA.regexp)
