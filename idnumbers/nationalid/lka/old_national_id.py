import re
from types import SimpleNamespace
from typing import Optional
from ..constant import Citizenship
from .national_id import NationalID, ParseResult


class OldIDParseResult(ParseResult):
    """old format contains more info"""
    citizenship: Citizenship


class OldNationalID:
    """
    LKA old National ID number format which is phased out on 2016
    # https://en.wikipedia.org/wiki/National_identification_number#Sri_Lanka
    # https://drp.gov.lk/Templates/Artical%20-%20English%20new%20number.html
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'LK',
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<year>\d{2})'
                             r'(?P<days>\d{3})'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)'
                             r'(?P<citizenship>[XxVv])$'),
        'alias_of': None,
        'names': ['National ID Number'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Sri_Lanka',
                  'https://drp.gov.lk/Templates/Artical%20-%20English%20new%20number.html'],
        'deprecated': True
    })

    @staticmethod
    def to_new(id_number: str) -> Optional[str]:
        """convert the old format to the new format"""
        match_obj = OldNationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        year = match_obj.group('year')
        days = match_obj.group('days')
        sn = match_obj.group('sn')
        checksum = match_obj.group('checksum')
        return f'19{year}{days}0{sn}{checksum}'

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the old format id numbers
        """
        if not id_number:
            return False

        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return OldNationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[OldIDParseResult]:
        """it converts to new format and parse the extra citizen value"""
        new_id_num = OldNationalID.to_new(id_number)
        if not new_id_num:
            return None
        result = NationalID.parse(new_id_num)
        if not result:
            return None
        citizenship = Citizenship.CITIZEN if id_number[-1].upper() == 'V' else Citizenship.RESIDENT
        return {
            **result,
            'citizenship': citizenship
        }

    @staticmethod
    def checksum(id_number) -> bool:
        """use new format to check the checksum"""
        new_id_num = OldNationalID.to_new(id_number)
        if not new_id_num:
            return False
        return NationalID.checksum(new_id_num)
