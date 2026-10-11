import re
from typing import Optional, TypedDict

from ..metadata import IdMetadata
from ..util import match_regexp

_RENAP = ('https://www.renap.gob.gt/sites/default/files/boletines-publicaciones/'
          'inforenap_163_-_08042021_-_que_es_el_cui.pdf')


class ParseResult(TypedDict):
    """The CUI fields as printed, preserving leading zeroes."""
    correlative: str
    """the eight system-assigned digits, not checked for issuance"""
    check_digit: str
    """the verification digit, returned unverified"""
    department: str
    """the two-digit department-of-birth code, not decoded"""
    municipality: str
    """the two-digit municipality-of-birth code, not decoded"""


class DPI:
    """
    Guatemala Código Único de Identificación (CUI), printed on the Documento Personal de Identificación (DPI).

    RENAP bulletin 163 (8 April 2021) defines the 13-digit layout: eight system-assigned digits, one verification
    digit, two department-of-birth digits and two municipality-of-birth digits. The source is in ``METADATA.links``.

    Validation is deliberately structure-only: exactly 13 ASCII digits, department 01-22 and municipality 01-99.
    The ranges are the maintainer-approved policy in issue #333, not rules established by that RENAP bulletin.
    No per-department municipality table or check-digit algorithm is verified, so neither is enforced. Any
    verification digit and a zero correlative are accepted. ``parse()`` preserves all four fields as strings;
    ``check_digit`` is unverified. ``METADATA.checksum`` is ``False`` and there is no ``checksum()`` method.
    This does not establish issuance, authenticity or a department/municipality combination's existence.

    Only compact input is accepted: whitespace, separators and trailing newlines are rejected. Unlike the
    Node.js sister project's whitespace normalization, this follows Python's strict malformed-input contract.
    Optional UI formatting/normalization helpers do not change the validator's policy.
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'GT',
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<correlative>[0-9]{8})(?P<check_digit>[0-9])'
                             r'(?P<department>0[1-9]|1[0-9]|2[0-2])(?P<municipality>0[1-9]|[1-9][0-9])$'),
        'alias_of': None,
        'names': ['Código Único de Identificación', 'Documento Personal de Identificación', 'CUI', 'DPI'],
        'links': [_RENAP, 'https://github.com/identique/idnumbers/issues/333#issuecomment-6105364701'],
        'deprecated': False,
        'country_name': 'Guatemala',
        'id_type': 'National ID Number',
        'official_name': 'Código Único de Identificación',
        'display_format': 'NNNNNNNNVDDMM',
        'example': '1912345670101',
        'checksum_algorithm': None,
        'masks': ('#############',),
    })
    """metadata of this id; the example is synthetic"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """Check the compact structure only, not the verification digit or issuance."""
        return DPI.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """Return zero-preserving fields, or ``None`` for malformed input."""
        match_obj = match_regexp(id_number, DPI.METADATA.regexp)
        if match_obj is None:
            return None
        return {
            'correlative': match_obj.group('correlative'),
            'check_digit': match_obj.group('check_digit'),
            'department': match_obj.group('department'),
            'municipality': match_obj.group('municipality'),
        }
