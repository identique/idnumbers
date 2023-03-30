import re
from types import SimpleNamespace
from ..util import validate_regexp
from .util import normalize


class DriverLicenseNumber:
    """
    Australia driver license number format
    https://learn.microsoft.com/en-us/microsoft-365/compliance/sit-defn-australia-drivers-license-number?view=o365-worldwide
    https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/library-of-system-data-identifiers-v95989112-d327e56315/australia-driver-s-license-number-v130004514-d327e56830.html
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AU',
        # length without insignificant chars
        'min_length': 6,
        'max_length': 10,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^('
                             r'\d{9}|\d{3} \d{3} \d{3}|'
                             r'\d{8}|\d{2} \d{3} \d{3}|'
                             r'[A-Za-z]\d{5}|'
                             r'\d{10}|\d{3}-\d{3}-\d{4}'
                             r')$'),
        'alias_of': None,
        'names': ['Driver Licence Number'],
        'links': [
            'https://learn.microsoft.com/en-us/microsoft-365/compliance/'
            'sit-defn-australia-drivers-license-number?view=o365-worldwide',
            'https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/'
            'data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/'
            'library-of-system-data-identifiers-v95989112-d327e56315/'
            'australia-driver-s-license-number-v130004514-d327e56830.html'],
        'deprecated': False
    })

    BLACK_TRAILING_NUMBER = ['00000', '11111', '22222', '33333', '44444', '55555', '66666', '77777', '88888', '99999']
    """black list for some numbers"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the AUS driver license number
        """
        if not validate_regexp(id_number, DriverLicenseNumber.METADATA.regexp):
            return False
        return normalize(id_number)[-5:] not in DriverLicenseNumber.BLACK_TRAILING_NUMBER
