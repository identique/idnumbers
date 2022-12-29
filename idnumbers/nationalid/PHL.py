import re
from types import SimpleNamespace
from .util import validate_regexp


class NationalID:
    """
    Philippines National ID number, PCN
    https://en.wikipedia.org/wiki/National_identification_number#Philippines
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'PH',
        # length without insignificant chars
        'min_length': 12,
        'max_length': 12,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^(\d{4}[ -]?\d{7}[ -]?\d)$')

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the PHL id number
        """
        return validate_regexp(id_number, NationalID.METADATA.regexp)
