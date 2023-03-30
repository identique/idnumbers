import re
from types import SimpleNamespace
from typing import Optional

from ..util import validate_regexp
from .old_national_id import OldNationalID, OldParseResult


class ParseResult(OldParseResult):
    yyyy: str
    """birth year"""


class NationalID(OldNationalID):
    """
    Bangladesh National ID number, জাতীয় পরিচয়পত্র, NID, BD
    https://en.wikipedia.org/wiki/National_identity_card_(Bangladesh)
    http://nationalidcardbangladesh.blogspot.com/2016/04/voter-id-national-id-card-number.html
    https://www.facebook.com/428195627559147/photos/a.428251897553520/428251617553548/?type=3
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BD',
        # length without insignificant chars
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<yyyy>\d{4})'
                             r'(?P<distinct>\d{2})'
                             r'(?P<rmo>\d)'
                             r'(?P<police>\d{2})'
                             r'(?P<union>\d{2})'
                             r'(?P<sn>\d{6})$'),
        'alias_of': None,
        'names': ['Bangladesh national ID number',
                  'জাতীয় পরিচয়পত্র',
                  'NID',
                  'BD'],
        'links': [
            'https://en.wikipedia.org/wiki/National_identity_card_(Bangladesh)',
            'http://nationalidcardbangladesh.blogspot.com/2016/04/voter-id-national-id-card-number.html',
            'https://www.facebook.com/428195627559147/photos/a.428251897553520/428251617553548/?type=3'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """
        Parse the result
        """
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        old_result = OldNationalID.parse(id_number[4:])
        if not old_result:
            return None
        return {
            **old_result,
            'yyyy': int(id_number[0:4])
        }
