import re
from ..util import birth_date as _calendar_date
from datetime import date
from ..metadata import IdMetadata
from typing import Optional, TypedDict, cast
from ..util import CHECK_DIGIT, validate_regexp, match_regexp


class ParseResult(TypedDict):
    """The parse result of Iceland ID"""

    yyyymmdd: date
    """dob"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """the ninth digit as printed; it is not verified, because kennitölur issued since 18 February 2026 have no
    calculated check digit"""


class IcelandicID:
    """
    Iceland Icelandic identification number, kennitala
    https://en.wikipedia.org/wiki/Icelandic_identification_number

    The number has 10 digits, ``DDMMYY-SSKC``: the date of birth, two serial digits, a ninth digit and the century
    digit. Þjóðskrá (Registers Iceland) says the last digit is 8, 9 or 0 and gives the century of birth, so ``C`` is 8
    for 1800-1899, 9 for 1900-1999 and 0 for 2000-2099.

    The ninth digit is not checked. Since 18 February 2026, Þjóðskrá issues every kennitala, both those of individuals
    registered in Þjóðskrá and system kennitölur, without a calculated check digit (*vartala*), and it asks systems to
    remove the check-digit test. The number carries no issue date, so a kennitala issued before that date, whose ninth
    digit is a mod-11 check digit, cannot be told apart from a new one. ``METADATA.checksum`` is ``False`` and there is
    no ``checksum()`` method. Þjóðskrá's six synthetic test kennitölur without a check digit, such as ``281191-3049``,
    validate.

    ``validate()`` checks the 10 ASCII digits (with an optional hyphen after the date), the century digit and that
    the date of birth is a real calendar date. Kennitölur of legal entities (day of registration + 40) are not
    supported.

    Sources:

    - Þjóðskrá, Um kennitölur (layout, century digit, the pre-2026 check digit and the 2026 change):
      https://www.skra.is/folk/eg-i-thjodskra/um-kennitolur/
    - Þjóðskrá, Allar kennitölur án vartölu (14 May 2025):
      https://www.skra.is/um-okkur/frettir/frett/2025/05/14/Kennitolur-an-vartolu/
    - Þjóðskrá, Gervigögn Þjóðskrár (test kennitölur without a check digit):
      https://www.skra.is/gogn/gervigogn-thjodskrar/
    """

    METADATA = IdMetadata(
        **{
            "iso3166_alpha2": "IS",
            "min_length": 10,
            "max_length": 10,
            "parsable": True,
            "checksum": False,
            "regexp": re.compile(
                r"^(?P<dd>\d{2})(?P<mm>\d{2})(?P<yy>\d{2})-?"
                r"(?P<sn>\d{2})"
                r"(?P<checksum>\d)"
                r"(?P<century>\d)$"
            ),
            "alias_of": None,
            "names": ["Icelandic identification number", "kennitala", "kt."],
            "links": [
                "https://en.wikipedia.org/wiki/Icelandic_identification_number",
                "https://www.skra.is/folk/eg-i-thjodskra/um-kennitolur/",
                "https://www.skra.is/um-okkur/frettir/frett/2025/05/14/Kennitolur-an-vartolu/",
                "https://www.skra.is/gogn/gervigogn-thjodskrar/",
            ],
            "deprecated": False,
            "country_name": "Iceland",
            "id_type": "Icelandic Identification Number",
            "official_name": "kennitala",
            "display_format": "DDMMYY-SSKC",
            "example": "120174-3399",
            "checksum_algorithm": None,
            "masks": ("######-####",),
        }
    )

    CENTURY_MAP = {"8": 1800, "9": 1900, "0": 2000}
    """the first year of the century of birth, by the last digit"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate"""
        if not validate_regexp(id_number, IcelandicID.METADATA.regexp):
            return False
        return IcelandicID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = match_regexp(id_number, IcelandicID.METADATA.regexp)
        if not match_obj:
            return None
        year_base = IcelandicID.CENTURY_MAP.get(match_obj.group("century"))
        if year_base is None:
            return None
        yy = int(match_obj.group("yy"))
        mm = int(match_obj.group("mm"))
        dd = int(match_obj.group("dd"))
        try:
            calendar_date = _calendar_date(yy + year_base, mm, dd)
            if calendar_date is None:
                return None
            return {
                "yyyymmdd": calendar_date,
                "sn": match_obj.group("sn"),
                "checksum": cast(CHECK_DIGIT, int(match_obj.group("checksum"))),
            }
        except ValueError:
            # catch the date error
            return None
