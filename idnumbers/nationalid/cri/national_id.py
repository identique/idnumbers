import re
from ..metadata import IdMetadata
from typing import Dict, Optional, TypedDict
from ..util import validate_regexp, match_regexp


PROVINCE_NAMES: Dict[int, str] = {
    1: 'San José',
    2: 'Alajuela',
    3: 'Cartago',
    4: 'Heredia',
    5: 'Guanacaste',
    6: 'Puntarenas',
    7: 'Limón',
    8: 'Naturalized',
    9: 'Partida Especial de Nacimientos',
}
"""Meaning of the leading digit of a cédula.

Digits 1 to 7 are the seven provinces of birth (the *partido* where the birth was registered), 8 marks a naturalized
citizen and 9 the special birth register (*Partida Especial de Nacimientos*), see pages 23-24 of the TSE booklet
cited in :class:`NationalID`.
"""


class ParseResult(TypedDict):
    """The parse result of Costa Rica cédula de identidad"""
    province: int
    """the leading *partido* digit, 1 to 9; see :data:`PROVINCE_NAMES`"""
    province_name: str
    """the meaning of the leading digit, for example ``San José`` for 1"""
    tomo: str
    """the *tomo* (register volume) number, 4 digits, zero-padded"""
    asiento: str
    """the *asiento* (register entry) number, 4 digits, zero-padded: the last four digits of the entry"""


class NationalID:
    """
    Costa Rica cédula de identidad (cédula física), issued by the Registro Civil of the Tribunal Supremo de
    Elecciones (TSE).

    The number has the form ``P-TTTT-AAAA``: the *partido* digit ``P`` (1 to 7 for the province of birth, 8 for
    naturalized citizens, 9 for the special birth register), the *tomo* ``TTTT`` and the *asiento* ``AAAA`` of the
    birth registration. A TSE agreement of 25 October 1956 keeps only the last four digits of an *asiento* longer
    than four digits, and the card prints the tomo and asiento zero-padded to four digits each.

    There is no check digit; the TSE confirms a number by looking it up in the Registro Civil. ``validate()``
    therefore checks the layout only. Hyphens are optional, so ``1-0913-0259`` and ``109130259`` are both accepted.

    Deliberately not accepted:

    - python-stdnum's 10-digit ``0P-TTTT-AAAA`` form (for example ``0109130259``): the leading ``0`` is the
      persona física prefix of the Hacienda tax number, not part of the cédula, and a province ``0`` does not exist;
    - unpadded forms such as ``1-913-259``, which cannot be split into tomo and asiento unambiguously without the
      separators;
    - spaces and slashes as separators, and other numbers of the same country: the 10-digit cédula jurídica and the
      11 to 12-digit DIMEX.

    Sources:

    - Tribunal Supremo de Elecciones, *Documentos de identificación* (pages 23-24 and 46):
      https://www.tse.go.cr/pdf/fasciculos_capacitacion/documentos-de-identificacion.pdf
    - Ministerio de Hacienda, cédula formats: https://www.hacienda.go.cr/consultapagos/ayuda_cedulas.htm
    - https://en.wikipedia.org/wiki/Costa_Rican_identity_card
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'CR',
        'min_length': 9,
        'max_length': 9,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<province>[1-9])-?'
                             r'(?P<tomo>\d{4})-?'
                             r'(?P<asiento>\d{4})$'),
        'alias_of': None,
        'names': ['Cédula de Identidad',
                  'Cédula de Persona Física',
                  'Cédula Física'],
        'links': ['https://www.tse.go.cr/pdf/fasciculos_capacitacion/documentos-de-identificacion.pdf',
                  'https://www.hacienda.go.cr/consultapagos/ayuda_cedulas.htm',
                  'https://en.wikipedia.org/wiki/Costa_Rican_identity_card'],
        'deprecated': False,
        'country_name': 'Costa Rica',
        'id_type': 'Identity Card Number',
        'official_name': 'Cédula de Identidad',
        'display_format': '#-####-####',
        'example': '1-0234-0567',
        'checksum_algorithm': None,
        'masks': ('#-####-####', '#########')
    })
    """metadata of this id"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate"""
        return validate_regexp(id_number, NationalID.METADATA.regexp)

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = match_regexp(id_number, NationalID.METADATA.regexp)
        if not match_obj:
            return None
        province = int(match_obj.group('province'))
        return {
            'province': province,
            'province_name': PROVINCE_NAMES[province],
            'tomo': match_obj.group('tomo'),
            'asiento': match_obj.group('asiento'),
        }
