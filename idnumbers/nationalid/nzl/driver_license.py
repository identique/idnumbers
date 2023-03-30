import re
from types import SimpleNamespace
from ..util import validate_regexp
from .util import BLACK_TRAILING_NUMBER


class DriverLicenseNumber:
    """
    New Zealand driver license number format
    https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/library-of-system-data-identifiers-v95989112-d327e56315/new-zealand-driver-s-licence-number-v130004625-d327e90104/new-zealand-driver-s-licence-number-narrow-breadth-v130007408-d327e90179.html#v130007408
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'NZ',
        # length without insignificant chars
        'min_length': 8,
        'max_length': 8,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^\w{2}\d{6}$'),
        'alias_of': None,
        'names': ['Driver License'],
        'links': ['https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/'
                  'data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/'
                  'library-of-system-data-identifiers-v95989112-d327e56315/'
                  'new-zealand-driver-s-licence-number-v130004625-d327e90104/'
                  'new-zealand-driver-s-licence-number-narrow-breadth-v130007408-d327e90179.html#v130007408'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NZL driver license number
        """
        if not validate_regexp(id_number, DriverLicenseNumber.METADATA.regexp):
            return False
        return id_number[-6:] not in BLACK_TRAILING_NUMBER
