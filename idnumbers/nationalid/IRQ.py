import re
from types import SimpleNamespace
from .util import validate_regexp


class NationalID:
    """
    Iraq National Card number. not enough docs to research.
    https://en.wikipedia.org/wiki/Iraq_National_Card
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'IQ',
        'min_length': 12,
        'max_length': 12,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^\d{12}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        return validate_regexp(id_number, NationalID.METADATA.regexp)
