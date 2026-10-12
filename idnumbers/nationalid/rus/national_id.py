import re
from typing import Optional, TypedDict

from ..metadata import IdMetadata
from ..util import match_regexp


class ParseResult(TypedDict):
    """Zero-preserving fields of a Russian internal passport number."""

    series: str
    """The four-digit series, as printed."""
    number: str
    """The six-digit number, as printed."""


class NationalID:
    """
    Russian internal passport (Паспорт гражданина Российской Федерации).

    Clause 3 of the passport-blank description in Government Decree No. 2267 of 23 December 2023 specifies a
    four-digit series and a six-digit number, printed in three groups of two, two and six digits.
    This validator accepts exactly ten ASCII digits, ``SSSS NNNNNN``, or the printed ``SS SS NNNNNN`` layout,
    using literal single ASCII spaces only. It does not normalize arbitrary separators or whitespace.

    The all-zero series ``0000`` and number ``000000`` are rejected by maintainer policy in issue #334;
    these exclusions are not attributed to the decree. No checksum, region, year or allocation checks are
    performed. Structural acceptance does not establish issuance or authenticity. All examples are synthetic.

    Sources:

    - https://publication.pravo.gov.ru/document/0001202312290097 (official decree)
    - https://www.consultant.ru/document/cons_doc_LAW_466454/51d3a2d43a726e22847dd3be33f75c45c756b8a7/
      (passport-blank description, clause 3)
    - https://github.com/identique/idnumbers/issues/334#issuecomment-6106045930 (zero-field policy)
    """

    METADATA = IdMetadata(
        **{
            "iso3166_alpha2": "RU",
            "min_length": 10,
            "max_length": 10,
            "parsable": True,
            "checksum": False,
            "regexp": re.compile(r"^(?:[0-9]{10}|[0-9]{4} [0-9]{6}|[0-9]{2} [0-9]{2} [0-9]{6})$"),
            "alias_of": None,
            "names": ["Internal Passport", "Russian Internal Passport", "Паспорт гражданина Российской Федерации"],
            "links": [
                "https://publication.pravo.gov.ru/document/0001202312290097",
                "https://www.consultant.ru/document/cons_doc_LAW_466454/51d3a2d43a726e22847dd3be33f75c45c756b8a7/",
                "https://github.com/identique/idnumbers/issues/334#issuecomment-6106045930",
            ],
            "deprecated": False,
            "country_name": "Russia",
            "id_type": "Internal Passport",
            "official_name": "Паспорт гражданина Российской Федерации",
            "display_format": "SSSS NNNNNN",
            "example": "1234 567890",
            "checksum_algorithm": None,
            "masks": ("#### ######", "##########", "## ## ######"),
        }
    )
    """Metadata of this ID."""

    @staticmethod
    def validate(id_number: str) -> bool:
        """Check the exact layout and the nonzero-field policy, not issuance or authenticity."""
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """Return the series and number as strings, or ``None`` for a rejected input."""
        if not match_regexp(id_number, NationalID.METADATA.regexp):
            return None
        compact = id_number.replace(" ", "")
        series, number = compact[:4], compact[4:]
        if series == "0000" or number == "000000":
            return None
        return {"series": series, "number": number}
