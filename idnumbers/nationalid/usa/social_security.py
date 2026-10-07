import re
from ..metadata import IdMetadata

from ..util import validate_regexp


class SocialSecurityNumber:
    """
    United States Social Security number (SSN) format
    Metadata counts nine significant digits, excluding the two hyphens. Validation requires
    the 11-character printed layout: three digits, a hyphen, two digits, a hyphen and four digits.
    https://en.wikipedia.org/wiki/National_identification_number#United_States
    https://www.geeksforgeeks.org/how-to-validate-ssn-social-security-number-using-regular-expression/
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'US',
        # Significant digits only; the two required hyphens are excluded.
        'min_length': 9,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^(?!666|000|9\d{2})\d{3}-(?!00)\d{2}-(?!0{4})\d{4}$'),
        'alias_of': None,
        'names': ['Social Security number',
                  'SSN'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#United_States'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate USA Social Security number
        """
        return validate_regexp(id_number, SocialSecurityNumber.METADATA.regexp)
