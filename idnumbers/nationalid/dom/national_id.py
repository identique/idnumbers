import re
from ..metadata import IdMetadata
from typing import Optional, TypedDict
from ..util import CHECK_DIGIT, luhn_digit, match_regexp


class ParseResult(TypedDict):
    """The parse result of Dominican Republic cédula de identidad y electoral"""
    series: str
    """the first 3 digits; historically the issuing municipality, no current meaning is decoded"""
    sequence: str
    """the 7-digit sequence number, zero-padded"""
    checksum: CHECK_DIGIT
    """the last digit: the Luhn check digit of the first 10 digits"""


class NationalID:
    """
    Dominican Republic cédula de identidad y electoral, issued by the Junta Central Electoral (JCE) and used as the
    tax number of individuals by the Dirección General de Impuestos Internos (DGII).

    The number has 11 digits and is printed as ``NNN-NNNNNNN-C``: a 3-digit series, a 7-digit sequence number and
    a check digit. The check digit is the Luhn (mod 10) digit of the first ten digits, so the Luhn sum of all
    eleven digits is a multiple of 10. The DGII checks the same digit in its own tools and reports an alert for an
    incorrect check digit. ``validate()`` checks the layout and the check digit; hyphens are optional, so
    ``402-0000001-2`` and ``40200000012`` are both accepted.

    Deliberately not accepted:

    - spaces as separators (python-stdnum and the Node port strip them);
    - python-stdnum's list of about 576 issued cédulas that fail the Luhn check, for example ``00000021249``. It
      has no official source and it is made of real personal numbers, so it is not copied here; the question is
      tracked in https://github.com/identique/idnumbers/issues/517;
    - the 9-digit RNC (*Registro Nacional del Contribuyente*) of companies and other lengths.

    Sources:

    - python-stdnum, ``stdnum/do/cedula.py``:
      https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/do/cedula.py
    - Dirección General de Impuestos Internos, help article on the 607 format check ("11 dígitos para cédulas"
      and the incorrect check digit alert):
      https://ayuda.dgii.gov.do/conversations/formatos-de-envo-de-datos/ca3904-cules-son-las-principales-alertas-que-se-pueden-presentar-al-validar-el-formato-607-en-la-herramienta-de-excel/5f3c17998cd858ce87a20d04
    - https://en.wikipedia.org/wiki/Luhn_algorithm
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'DO',
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<series>\d{3})-?'
                             r'(?P<sequence>\d{7})-?'
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['Cédula de Identidad y Electoral',
                  'Cédula'],
        'links': ['https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/do/cedula.py',
                  'https://ayuda.dgii.gov.do/conversations/formatos-de-envo-de-datos/'
                  'ca3904-cules-son-las-principales-alertas-que-se-pueden-presentar-al-validar-el-formato-607-'
                  'en-la-herramienta-de-excel/5f3c17998cd858ce87a20d04',
                  'https://en.wikipedia.org/wiki/Luhn_algorithm'],
        'deprecated': False,
        'country_name': 'Dominican Republic',
        'id_type': 'Identity and Electoral Card Number',
        'official_name': 'Cédula de Identidad y Electoral',
        'display_format': '###-#######-#',
        'example': '402-1234567-8',
        'checksum_algorithm': 'Luhn (mod 10)',
        'masks': ('###-#######-#', '###########')
    })
    """metadata of this id"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the layout and the Luhn check digit"""
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result; ``None`` unless the number is valid"""
        match_obj = match_regexp(id_number, NationalID.METADATA.regexp)
        if not match_obj:
            return None
        checksum = NationalID.checksum(id_number)
        if checksum is None or str(checksum) != match_obj.group('checksum'):
            return None
        return {
            'series': match_obj.group('series'),
            'sequence': match_obj.group('sequence'),
            'checksum': checksum,
        }

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """
        calculate the Luhn check digit from the first 10 digits

        :return: the expected check digit, or ``None`` if the layout does not match. The number's own last digit is
            not compared; ``validate()`` does that.
        """
        match_obj = match_regexp(id_number, NationalID.METADATA.regexp)
        if not match_obj:
            return None
        digits = match_obj.group('series') + match_obj.group('sequence')
        return luhn_digit([int(char) for char in digits])
