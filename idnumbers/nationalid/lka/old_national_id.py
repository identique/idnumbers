import re
from ..metadata import IdMetadata
from typing import Optional
from ..constant import Citizenship
from .national_id import NationalID, ParseResult
from ..util import match_regexp


class OldIDParseResult(ParseResult):
    """Old format parse result; citizenship cannot be inferred from the voter suffix."""

    citizenship: Optional[Citizenship]


class OldNationalID:
    """
    LKA old National ID number format which is phased out on 2016

    The historical V/X suffix indicated voter/nonvoter status, not citizenship: nonvoters included underage
    citizens. A Canadian High Commission report reproduced by the IRB also notes that cards issued in 2007
    made no such distinction. The suffix is not a reliable statement of current voter eligibility.

    https://www.irb-cisr.gc.ca/en/country-information/rir/Pages/index.aspx?doc=451823

    # https://en.wikipedia.org/wiki/National_identification_number#Sri_Lanka
    # https://drp.gov.lk/Templates/Artical%20-%20English%20new%20number.html
    """

    METADATA = IdMetadata(
        **{
            "iso3166_alpha2": "LK",
            "min_length": 10,
            "max_length": 10,
            "parsable": True,
            "checksum": True,
            "regexp": re.compile(
                r"^(?P<year>\d{2})"
                r"(?P<days>\d{3})"
                r"(?P<sn>\d{3})"
                r"(?P<checksum>\d)"
                r"(?P<citizenship>[XxVv])$"
            ),
            "alias_of": None,
            "names": ["National ID Number"],
            "links": [
                "https://en.wikipedia.org/wiki/National_identification_number#Sri_Lanka",
                "https://drp.gov.lk/Templates/Artical%20-%20English%20new%20number.html",
                "https://www.irb-cisr.gc.ca/en/country-information/rir/Pages/index.aspx?doc=451823",
            ],
            "deprecated": True,
            "country_name": "Sri Lanka",
            "id_type": "National Identity Card Number (Old)",
            "official_name": None,
            "display_format": "YYDDDSSSCV",
            "example": "900120001V",
            "checksum_algorithm": "The check digit of the new 12-digit number that the old number converts to (weights 8, "
            "4, 3, 2, 7, 6, 5, 7, 4, 3, 2 mod 11)",
            "masks": ("#########L",),
        }
    )

    @staticmethod
    def to_new(id_number: str) -> Optional[str]:
        """convert the old format to the new format"""
        match_obj = match_regexp(id_number, OldNationalID.METADATA.regexp)
        if not match_obj:
            return None
        year = match_obj.group("year")
        days = match_obj.group("days")
        sn = match_obj.group("sn")
        checksum = match_obj.group("checksum")
        return f"19{year}{days}0{sn}{checksum}"

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the old format id numbers
        """
        if not isinstance(id_number, str) or not id_number:
            return False
        return OldNationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[OldIDParseResult]:
        """Parse via the new format, retaining the citizenship key with an unknown (None) value."""
        new_id_num = OldNationalID.to_new(id_number)
        if not new_id_num:
            return None
        result = NationalID.parse(new_id_num)
        if not result:
            return None
        # V/X historically described voter eligibility, not citizenship (including underage citizen nonvoters).
        return {**result, "citizenship": None}

    @staticmethod
    def checksum(id_number: str) -> bool:
        """use new format to check the checksum"""
        new_id_num = OldNationalID.to_new(id_number)
        if not new_id_num:
            return False
        return NationalID.checksum(new_id_num)
