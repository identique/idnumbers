import re
from types import SimpleNamespace
from .util import validate_regexp


class NationalInsuranceNumber:
    """
    UK National Insurance Number format
    https://en.wikipedia.org/wiki/National_Insurance_number
    https://www.gov.uk/hmrc-internal-manuals/national-insurance-manual/nim39110
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'GB',
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^[A-Z]{2}\d{6}[A-Z]$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the GBR national insurance number
        """
        if not validate_regexp(id_number, NationalInsuranceNumber.METADATA.regexp):
            return False
        return (NationalInsuranceNumber.__check_prefix(id_number[:2]) and
                NationalInsuranceNumber.__check_suffix(id_number[-1]))

    @staticmethod
    def __check_prefix(prefix: str) -> bool:
        # These characters are not used as either the first or second letter of a NINO prefix
        prohibit_chars = ['D', 'F', 'I', 'Q', 'U', 'V']
        first_check = [True for i in prohibit_chars if i in prefix]
        if first_check:
            return False
        # The letter O is not used as the second letter of a prefix
        if 'O' in prefix[1]:
            return False
        # These codes are not to be used
        not_allocated_codes = ['BG', 'GB', 'NK', 'KN', 'TN', 'NT', 'ZZ']
        if prefix in not_allocated_codes:
            return False
        return True

    @staticmethod
    def __check_suffix(suffix: str) -> bool:
        allowed_suffix = ['A', 'B', 'C', 'D', 'F', 'M', 'P']
        return suffix in allowed_suffix
