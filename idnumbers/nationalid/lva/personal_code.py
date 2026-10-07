import re
from types import SimpleNamespace
from typing import Optional, cast

from ..util import CHECK_DIGIT, validate_regexp
from .util import normalize


class PersonalCode:
    """
    Latvia Personal Code format, personas kods

    Legacy codes encode a valid DDMMYY date and century 0/1/2 (1800/1900/2000).
    Modern codes start with 32-39 and do not encode a date or century, under
    section 6(2) and transitional provision 4 of the Law on the Register of Natural Persons:
    https://likumi.lv/ta/id/296185
    https://www.pmlp.gov.lv/en/change-personal-identity-number
    https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/latvia-tin.pdf

    These sources establish date/prefix rules, not a modern checksum requirement.
    The existing checksum behaviour is retained pending clarification in issue #440.
    https://github.com/identique/idnumbers/issues/440
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'LV',
        # length without insignificant chars
        'min_length': 11,
        'max_length': 11,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{6}-?\d{5}$)'),
        'alias_of': None,
        'names': ['Personal Code',
                  'personas kods'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Latvia',
                  'https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/Latvia-TIN.pdf',
                  'https://likumi.lv/ta/id/296185',
                  'https://www.pmlp.gov.lv/en/change-personal-identity-number',
                  'https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/latvia-tin.pdf'],
        'deprecated': False
    })

    MULTIPLIER = [1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    """multiplier for checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        check_digit = PersonalCode.checksum(id_number)
        # checksum() is None unless the input is a str that matches the regexp, so [-1] is safe below
        if check_digit is None or str(check_digit) != id_number[-1]:
            return False
        prefix = int(normalize(id_number)[:2])
        if 32 <= prefix <= 39:
            return True
        if not 1 <= prefix <= 31:
            return False
        # Local import avoids the cycle: OldPersonalCode uses PersonalCode.checksum().
        from .old_personal_code import OldPersonalCode
        return OldPersonalCode.validate(id_number)

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """
        Calculate national id checksum: (1101-sum) mod 11 and mod 10.
        None is returned if the input does not match the format.
        """
        if not validate_regexp(id_number, PersonalCode.METADATA.regexp):
            return None
        numbers = [int(i) for i in normalize(id_number)[:10]]
        weighted_value = sum([value * PersonalCode.MULTIPLIER[index] for (index, value) in enumerate(numbers)])
        return cast(CHECK_DIGIT, (1101 - weighted_value) % 11 % 10)
