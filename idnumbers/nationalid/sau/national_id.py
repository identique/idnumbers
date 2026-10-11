import re
from typing import Optional, TypedDict

from ..constant import Citizenship
from ..metadata import IdMetadata
from ..util import match_regexp

_NPHIES = 'https://portal.nphies.sa/ig/StructureDefinition-patient.html'


class ParseResult(TypedDict):
    """The holder category implied by the first digit."""
    citizenship: Citizenship
    """``CITIZEN`` for a leading ``1`` (national ID), ``RESIDENT`` for a leading ``2`` (Iqama)"""


class NationalID:
    """
    Saudi Arabia national ID number (رقم الهوية الوطنية) and resident identity / Iqama number (رقم الإقامة).

    The Council of Health Insurance (CHI) NPHIES FHIR implementation guide, Patient profile, constrains the
    identifier with business validations ``BV-00797`` (national ID: the value starts with ``1`` and has length
    10) and ``BV-00798`` (Iqama: the value starts with ``2`` and has length 10). The source is in
    ``METADATA.links``.

    Validation is deliberately structure-only, as decided by the maintainer in issue #335: exactly 10 ASCII
    digits whose first digit is ``1`` (Saudi citizen) or ``2`` (resident). ``parse()`` returns the matching
    ``Citizenship``. The last digit is not verified, because no authoritative source for a check digit was
    found: the Luhn rule proposed in the issue is unconfirmed, so Luhn-failing numbers are accepted.
    ``METADATA.checksum`` is ``False`` and there is no ``checksum()`` method.
    Acceptance does not establish issuance or authenticity.

    Only compact input is accepted: whitespace, separators, trailing newlines and non-ASCII digits are rejected.
    This deliberately differs from the Node.js sister project, which strips spaces and hyphens and enforces Luhn.
    All examples are synthetic.

    Sources:

    - https://portal.nphies.sa/ig/StructureDefinition-patient.html (NPHIES Patient profile, BV-00797 / BV-00798)
    - https://github.com/identique/idnumbers/issues/335#issuecomment-6107912284 (structure-only decision)
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'SA',
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<type>[12])[0-9]{9}$'),
        'alias_of': None,
        'names': ['National ID', 'Iqama', 'Resident Identity', 'رقم الهوية الوطنية', 'رقم الإقامة'],
        'links': [_NPHIES, 'https://github.com/identique/idnumbers/issues/335#issuecomment-6107912284'],
        'deprecated': False,
        'country_name': 'Saudi Arabia',
        'id_type': 'National ID Number',
        'official_name': 'رقم الهوية الوطنية',
        'display_format': 'TNNNNNNNNN',
        'example': '1000000008',
        'checksum_algorithm': None,
        'masks': ('##########',),
    })
    """Metadata of this ID; the example is synthetic."""

    @staticmethod
    def validate(id_number: str) -> bool:
        """Check the compact structure only, not a check digit, issuance or authenticity."""
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """Return the citizenship implied by the first digit, or ``None`` for malformed input."""
        match_obj = match_regexp(id_number, NationalID.METADATA.regexp)
        if match_obj is None:
            return None
        citizenship = Citizenship.CITIZEN if match_obj.group('type') == '1' else Citizenship.RESIDENT
        return {'citizenship': citizenship}
