import re
from types import SimpleNamespace

from ..util import validate_regexp


class CitizenIDNumber:
    """
    Slovakia Citizen Identification Card Number format, Číslo občianskeho preukazu (ČOP)
    https://en.wikipedia.org/wiki/National_identification_number#Slovakia
    https://en.wikipedia.org/wiki/Slovak_identity_card
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'SK',
        'min_length': 8,
        'max_length': 8,
        # length without insignificant chars
        'parsable': False,
        # has parse function
        'checksum': False,
        # has checksum function
        'regexp': re.compile(r'^[A-Z]{2} ?\d{6}$'),
        # regular expression to validate the id
        'alias_of': None,
        'names': ['Citizen Identification Card Number',
                  'Číslo občianskeho preukazu',
                  'ČOP'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Slovakia',
                  'https://en.wikipedia.org/wiki/Slovak_identity_card'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate CitizenIDNumber
        """
        return validate_regexp(id_number, CitizenIDNumber.METADATA.regexp)
