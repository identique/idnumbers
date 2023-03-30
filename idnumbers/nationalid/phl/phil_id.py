import re
from types import SimpleNamespace
from ..util import validate_regexp


class PhilID:
    """
    Philippines PhilID Card Number, PCN
    https://en.wikipedia.org/wiki/National_identification_number#Philippines
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'PH',
        # length without insignificant chars
        'min_length': 12,
        'max_length': 12,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^(\d{4}[ -]?\d{7}[ -]?\d)$'),
        'alias_of': None,
        'names': ['PhilID Card Number',
                  'PCN',
                  'PhilSys'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Philippines',
                  'https://en.wikipedia.org/wiki/Philippine_national_identity_card'],
        'deprecated': False

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the PHL id number
        """
        return validate_regexp(id_number, PhilID.METADATA.regexp)
