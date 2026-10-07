import re
from types import SimpleNamespace
from ..util import validate_regexp


class PhilID:
    """
    Philippine national identification: the 12-digit PhilSys Number (PSN),
    not the separate 16-digit PhilID Card Number (PCN). The public class name PhilID is retained.
    Metadata counts significant digits only. Validation retains the compact format or optional
    spaces/hyphens after the fourth and eleventh digits.
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
        'names': ['PhilSys Number',
                  'PSN',
                  'Philippine National ID'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Philippines',
                  'https://en.wikipedia.org/wiki/Philippine_national_identity_card',
                  'https://psa.gov.ph/content/psa-bsp-promote-philid-card-security-and-verification-features'],
        'deprecated': False

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the PHL id number
        """
        return validate_regexp(id_number, PhilID.METADATA.regexp)
