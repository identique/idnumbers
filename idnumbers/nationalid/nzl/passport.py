import re
from types import SimpleNamespace
from ..util import validate_regexp
from .util import BLACK_TRAILING_NUMBER


class PassportNumber:
    """
    New Zealand passport number format
    https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/library-of-system-data-identifiers-v95989112-d327e56315/new-zealand-passport-number-v130004628-d327e90423/new-zealand-passport-number-narrow-breadth-v130007458-d327e90528.html
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'NZ',
        # length without insignificant chars
        'min_length': 7,
        'max_length': 8,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^([Ll][Aa]|[Ll][Dd]|[Ll][Ff]|[Nn]|[Ee][Aa]|[Ll][Hh])\d{6}$'),
        'alias_of': None,
        'names': ['Passport Number',
                  'NIN'],
        'links': ['https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/'
                  'data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/'
                  'library-of-system-data-identifiers-v95989112-d327e56315/'
                  'new-zealand-passport-number-v130004628-d327e90423/'
                  'new-zealand-passport-number-narrow-breadth-v130007458-d327e90528.html'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NZL passport number
        """
        if not validate_regexp(id_number, PassportNumber.METADATA.regexp):
            return False
        return id_number[-6:] not in BLACK_TRAILING_NUMBER
