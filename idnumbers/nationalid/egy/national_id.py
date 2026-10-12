import re
from datetime import date
from ..metadata import IdMetadata
from typing import Optional, TypedDict
from ..util import birth_date as _calendar_date, match_regexp

_ART_3 = (
    "https://lawyeregypt.net/%D8%A7%D9%84%D9%84%D8%A7%D8%A6%D8%AD%D8%A9-%D8%A7%D9%84%D8%AA%D9%86%D9%81%D9%8A"
    "%D8%B0%D9%8A%D8%A9-%D9%84%D9%82%D8%A7%D9%86%D9%88%D9%86-%D8%A7%D9%84%D8%A3%D8%AD%D9%88%D8%A7%D9%84-"
    "%D8%A7%D9%84%D9%85/"
)


class ParseResult(TypedDict):
    """The parse result of the Egypt national ID number"""

    yyyymmdd: date
    """the date of birth"""
    governorate: str
    """the 2-digit governorate-of-birth code, as printed; it is not decoded"""
    sn: str
    """the 4-digit serial number, zero-padded"""
    check_digit: str
    """the final digit as printed; it is not verified, because no check-digit algorithm is published"""


class NationalID:
    """
    Egypt national ID number (*al-raqm al-qawmi*, الرقم القومي), issued by the Civil Status Organization of the
    Ministry of Interior.

    The number has 14 digits, ``CYYMMDDGGSSSSV``, and Article 3 of the Executive Regulations of the Civil Status
    Law No. 143 of 1994 (Minister of Interior Decree No. 1121 of 1995) defines the layout: the first digit is the
    century of birth, the next six digits are the date of birth, two digits are the governorate of birth, four
    digits are a serial number and the last digit is an optional digit that confirms the number.

    ``validate()`` checks:

    - 14 ASCII digits and nothing else;
    - a century digit of 2 (the years 1900-1999) or 3 (the years 2000-2099). The regulation does not list the
      century values; this reading is the one commonly published (for example on Wikipedia) and it is the only way
      to read the century digit as a year;
    - that ``YYMMDD`` with that century is a real calendar date, so 29 February is accepted in leap years only.
      A date in the future is not rejected, because no source says it should be.

    Deliberately not validated or decoded, because no official source publishes the rule:

    - the governorate code: any two digits are accepted. The governorate table (01 Cairo, 02 Alexandria, ... 88
      born abroad) comes from Wikipedia and community libraries, not from the regulation;
    - the gender, commonly read from the parity of the serial number (odd for male, even for female): the same
      limitation, so ``parse()`` returns no gender;
    - the final digit: the regulation says it is optional and does not define it, and no check-digit algorithm is
      published. Third-party sources assert a Luhn or a weighted mod-11 check digit, but none cites an official
      source. The Node.js sister project's research note (not an official source; see below) reports that Luhn
      does not reproduce real check digits, while the weighted mod-11 hypothesis remains unproven. Therefore
      ``METADATA.checksum`` is ``False`` and there is no ``checksum()`` method. ``parse()`` returns the digit
      unverified.

    Sources:

    - Executive Regulations of the Civil Status Law No. 143 of 1994, Article 3 (Arabic text), as published at
      https://lawyeregypt.net/ (the full link is in ``METADATA.links``)
    - https://en.wikipedia.org/wiki/Egyptian_National_Identity_Card (century digit and governorate table; not
      official)
    - identique/idnumbers-npm research note on the Egyptian national ID (checksum investigation; not official):
      https://github.com/identique/idnumbers-npm/blob/main/docs/research/egypt-national-id.md
    """

    METADATA = IdMetadata(
        **{
            "iso3166_alpha2": "EG",
            "min_length": 14,
            "max_length": 14,
            "parsable": True,
            "checksum": False,
            "regexp": re.compile(
                r"^(?P<century>[23])"
                r"(?P<yy>\d{2})"
                r"(?P<mm>\d{2})"
                r"(?P<dd>\d{2})"
                r"(?P<governorate>\d{2})"
                r"(?P<sn>\d{4})"
                r"(?P<check_digit>\d)$"
            ),
            "alias_of": None,
            "names": ["National ID Number", "الرقم القومي"],
            "links": [_ART_3, "https://en.wikipedia.org/wiki/Egyptian_National_Identity_Card"],
            "deprecated": False,
            "country_name": "Egypt",
            "id_type": "National ID Number",
            "official_name": "الرقم القومي",
            "display_format": "CYYMMDDGGSSSSV",
            "example": "29001010100017",
            "checksum_algorithm": None,
            "masks": ("##############",),
        }
    )
    """metadata of this id"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the layout, the century digit and the calendar date of birth"""
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result; ``None`` unless the number is valid"""
        match_obj = match_regexp(id_number, NationalID.METADATA.regexp)
        if not match_obj:
            return None
        century = 1900 if match_obj.group("century") == "2" else 2000
        birthday = _calendar_date(
            century + int(match_obj.group("yy")), int(match_obj.group("mm")), int(match_obj.group("dd"))
        )
        if birthday is None:
            return None
        return {
            "yyyymmdd": birthday,
            "governorate": match_obj.group("governorate"),
            "sn": match_obj.group("sn"),
            "check_digit": match_obj.group("check_digit"),
        }
