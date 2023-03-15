import re
from enum import Enum
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'/\(\)', '', id_number)


class DocType(Enum):
    FIRST_GEN = 'first generation'
    MCA = 'macau civil authority'
    MPSP = 'macau public security police'
    ENTITY = 'entity'
    CI = 'commercial individual'


class ParseResult(TypedDict):
    """parse result for Identification Number"""
    doc_type: DocType
    """issuer"""
    sn: str
    """serial number"""


class NationalID:
    """
    Macau National ID number format, Permanent Resident Identity Card (BIRP),
    and Non-Permanent Resident Identity Card (BIRNP).
    https://en.wikipedia.org/wiki/National_identification_number#Macau
    https://en.wikipedia.org/wiki/Macau_Resident_Identity_Card
    https://validatetin.com/macao/
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'MO',
        'min_length': 8,
        'max_length': 8,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<doc_type>[01578])'
                             r'(?P<sn>\d{6})'
                             r'\(?(?P<extra>\d)\)?$')
    })

    TYPE_MAP = {'0': DocType.CI, '1': DocType.FIRST_GEN, '5': DocType.MCA, '7': DocType.MPSP, '8': DocType.ENTITY}

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """pares the result"""
        match_obj = NationalID.METADATA.regexp.match(id_number)

        if not match_obj:
            return None
        doc_type = match_obj.group('doc_type')
        sn = match_obj.group('sn')
        extra = match_obj.group('extra')
        try:
            return {
                'doc_type': NationalID.TYPE_MAP[doc_type],
                'sn': sn + extra
            }
        except ValueError:
            return None


BIRP = NationalID
"""alias of NationalID"""
BIRNP = NationalID
"""alias of NationalID"""
