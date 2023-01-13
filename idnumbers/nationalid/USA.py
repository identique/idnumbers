import re
from types import SimpleNamespace

from .util import validate_regexp


class SocialSecurityNumber:
    """
    United States Social Security number (SSN) format
    https://en.wikipedia.org/wiki/National_identification_number#United_States
    https://www.geeksforgeeks.org/how-to-validate-ssn-social-security-number-using-regular-expression/
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'US',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile("^(?!666|000|9\\d{2})\\d{3}-(?!00)\\d{2}-(?!0{4})\\d{4}$")
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate USA Social Security number
        """
        return validate_regexp(id_number, SocialSecurityNumber.METADATA.regexp)
