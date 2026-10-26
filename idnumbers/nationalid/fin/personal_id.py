import re
from ..util import birth_date as _calendar_date
from datetime import date
from ..metadata import IdMetadata
from typing import Literal, Optional, TypedDict, cast, get_args
from ..util import validate_regexp, match_regexp
from ..constant import Gender


CHECKSUM_TYPE = Literal[
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "H",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
]
"""literal for checksum type"""


class ParseResult(TypedDict):
    """The parse result of Finland personal identity code, HETU"""

    yyyymmdd: date
    """Birthday"""
    gender: Gender
    """Gender, male or female"""
    sn: str
    """The serial number born at the same date"""
    checksum: CHECKSUM_TYPE
    """checksum code in str"""


class PersonalIdentityCode:
    """
    Finland personal identity code, HETU
    https://en.wikipedia.org/wiki/National_identification_number#Finland

    The individual number (``SSS``) must be between 002 and 899. Government Decree 128/2010 § 2 defines it only as a
    three-digit number, odd for men and even for women, but DVV (the Digital and Population Data Services Agency) says
    that in practice all individual numbers issued are between 002 and 899. Numbers 900-999 are temporary codes, used
    for example in hospitals when a person's personal identity code is not known yet; DVV does not issue them and they
    are not recorded in the Population Information System. python-stdnum rejects the same numbers by default.

    Sources:

    - DVV, Personal identity code: https://dvv.fi/en/personal-identity-code
    - Government Decree on the Population Information System 128/2010, § 2:
      https://www.finlex.fi/fi/lainsaadanto/2010/128
    - Finnish Wikipedia, Henkilötunnus (temporary codes; not official):
      https://fi.wikipedia.org/wiki/Henkil%C3%B6tunnus
    """

    METADATA = IdMetadata(
        **{
            "iso3166_alpha2": "FI",
            "min_length": 11,
            "max_length": 11,
            "parsable": True,
            "checksum": True,
            "regexp": re.compile(
                r"^(?P<dd>\d{2})(?P<mm>\d{2})(?P<yy>\d{2})"
                r"(?P<century>[-+ABCDEFUVWXY])"
                r"(?P<sn>\d{3})"
                r"(?P<check>[0-9A-Z])$"
            ),
            "alias_of": None,
            "names": ["personal identity code", "HETU"],
            "links": [
                "https://en.wikipedia.org/wiki/National_identification_number#Finland",
                "https://dvv.fi/en/personal-identity-code",
                "https://www.finlex.fi/fi/lainsaadanto/2010/128",
            ],
            "deprecated": False,
            "country_name": "Finland",
            "id_type": "Personal Identity Code",
            "official_name": "henkilötunnus",
            "display_format": "DDMMYY{+-A}SSSC",
            "example": "131052-308T",
            "checksum_algorithm": "Mod 31 check character (the nine digits DDMMYYSSS as a number mod 31, mapped to 0-9 and "
            "A-Y without G, I, O, Q)",
            "masks": ("######*###X",),
        }
    )

    DOB_BASE_MAP = {
        "+": 1800,
        "-": 1900,
        "U": 1900,
        "V": 1900,
        "W": 1900,
        "X": 1900,
        "Y": 1900,
        "A": 2000,
        "B": 2000,
        "C": 2000,
        "D": 2000,
        "E": 2000,
        "F": 2000,
    }
    """ The century map for id """

    CHECKSUM_LIST = list(get_args(CHECKSUM_TYPE))
    """ possible checksum characteres """

    ISSUED_SN_RANGE = range(2, 900)
    """individual numbers DVV issues: 000 and 001 are not issued, and 900-999 are temporary codes"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the FIN id number
        """
        if not validate_regexp(id_number, PersonalIdentityCode.METADATA.regexp):
            return False
        return PersonalIdentityCode.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the FIN HETU id"""
        match_obj = match_regexp(id_number, PersonalIdentityCode.METADATA.regexp)
        if not match_obj:
            return None
        elif not PersonalIdentityCode.checksum(id_number):
            return None
        yy = int(match_obj.group("yy"))
        mm = int(match_obj.group("mm"))
        dd = int(match_obj.group("dd"))
        century = match_obj.group("century")
        sn = match_obj.group("sn")
        yyyy_base = PersonalIdentityCode.DOB_BASE_MAP[century]
        try:
            calendar_date = _calendar_date(yyyy_base + yy, mm, dd)
            if calendar_date is None:
                return None
            if int(sn) not in PersonalIdentityCode.ISSUED_SN_RANGE:
                return None
            return {
                "yyyymmdd": calendar_date,
                "gender": Gender.MALE if int(sn) % 2 == 1 else Gender.FEMALE,
                "sn": sn,
                "checksum": cast(CHECKSUM_TYPE, match_obj.group("check")),
            }
        except ValueError:
            return None

    @staticmethod
    def checksum(id_number: str) -> bool:
        """check if the ID valid against its checksum"""
        match_obj = match_regexp(id_number, PersonalIdentityCode.METADATA.regexp)
        if not match_obj:
            return False
        numbers = int(match_obj.group("dd") + match_obj.group("mm") + match_obj.group("yy") + match_obj.group("sn"))
        check_digit: str = PersonalIdentityCode.CHECKSUM_LIST[numbers % 31]
        return match_obj.group("check") == check_digit
