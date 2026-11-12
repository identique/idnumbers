import re
from ..metadata import IdMetadata
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

    PMLP specifies that the first digit is 3, the second is 2-9, and each remaining digit may be any
    digit from 0 to 9. The final digit is therefore not a check digit for modern codes.
    """

    METADATA = IdMetadata(
        **{
            "iso3166_alpha2": "LV",
            # length without insignificant chars
            "min_length": 11,
            "max_length": 11,
            # has parse function
            "parsable": False,
            # has checksum function
            "checksum": True,
            # regular expression to validate the id
            "regexp": re.compile(r"^(\d{6}-?\d{4}(?P<checksum>\d)$)"),
            "alias_of": None,
            "names": ["Personal Code", "personas kods"],
            "links": [
                "https://en.wikipedia.org/wiki/National_identification_number#Latvia",
                "https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/"
                "tax-identification-numbers/Latvia-TIN.pdf",
                "https://likumi.lv/ta/id/296185",
                "https://www.pmlp.gov.lv/en/change-personal-identity-number",
                "https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/latvia-tin.pdf",
            ],
            "deprecated": False,
            "country_name": "Latvia",
            "id_type": "Personal Code",
            "official_name": "personas kods",
            "display_format": "DDMMYY-SSSSS",
            "example": "161175-19997",
            "checksum_algorithm": "(1101 - weighted sum) mod 11 mod 10 for legacy only; "
            "weights 1, 6, 3, 7, 9, 10, 5, 8, 4, 2; modern codes have no check digit",
            "masks": ("######-#####", "###########"),
        }
    )

    MULTIPLIER = [1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    """multiplier for checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        if not validate_regexp(id_number, PersonalCode.METADATA.regexp):
            return False
        prefix = int(normalize(id_number)[:2])
        if 32 <= prefix <= 39:
            return True
        if not 1 <= prefix <= 31:
            return False
        # Local import avoids the cycle: OldPersonalCode uses PersonalCode._legacy_checksum().
        from .old_personal_code import OldPersonalCode

        return OldPersonalCode.validate(id_number)

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """
        Calculate the legacy national ID checksum: (1101-sum) mod 11 and mod 10.

        Modern numbers beginning with 32-39 have no check digit, so this returns None for them. None is also
        returned if the input does not match the format.
        """
        if not validate_regexp(id_number, PersonalCode.METADATA.regexp):
            return None
        prefix = int(normalize(id_number)[:2])
        if 32 <= prefix <= 39:
            return None
        return PersonalCode._legacy_checksum(id_number)

    @staticmethod
    def _legacy_checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """Calculate the original weighted checksum for any format-matching number."""
        if not validate_regexp(id_number, PersonalCode.METADATA.regexp):
            return None
        numbers = [int(i) for i in normalize(id_number)[:10]]
        weighted_value = sum([value * PersonalCode.MULTIPLIER[index] for (index, value) in enumerate(numbers)])
        return cast(CHECK_DIGIT, (1101 - weighted_value) % 11 % 10)
