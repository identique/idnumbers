import re
from ..util import birth_date as _calendar_date
from datetime import date
from ..metadata import IdMetadata
from typing import Literal, Optional, Tuple, TypedDict, Union, cast
from ..constant import Gender
from ..util import CHECK_DIGIT, validate_regexp, match_regexp
from .util import checksum


class IINParseResult(TypedDict):
    """The parse result of IIN"""
    yyyymmdd: date
    """dob"""
    gender: Gender
    """gender: male and female"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """check digit"""


class IndividualIDNumber:
    """
    Kazakhstan individual identification number, ЖСН, ZhSN, ИИН, IIN
    https://en.wikipedia.org/wiki/National_identification_number#Kazakhstan
    https://korgan-zan.kz/en/obtaining-iin-and-bin-in-kazakhstan/
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Kazakhstan-TIN.pdf
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'KZ',
        'min_length': 12,
        'max_length': 12,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<century>\d)'
                             r'(?P<sn>\d{4})'
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['Individual Identification Number',
                  'ЖСН',
                  'ZhSN',
                  'ИИН',
                  'IIN'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Kazakhstan',
                  'https://korgan-zan.kz/en/obtaining-iin-and-bin-in-kazakhstan/',
                  'https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/Kazakhstan-TIN.pdf',
                  'https://ru.wikipedia.org/wiki/'
                  '%D0%98%D0%BD%D0%B4%D0%B8%D0%B2%D0%B8%D0%B4%D1%83%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9_'
                  '%D0%B8%D0%B4%D0%B5%D0%BD%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D0%BE%D0%BD'
                  '%D0%BD%D1%8B%D0%B9_'
                  '%D0%BD%D0%BE%D0%BC%D0%B5%D1%80'],
        'deprecated': False,
        'country_name': 'Kazakhstan',
        'id_type': 'Individual Identification Number',
        'official_name': 'Индивидуальный идентификационный номер',
        'display_format': 'YYMMDDGSSSSC',
        'example': '900101300017',
        'checksum_algorithm': 'Weighted sum mod 11 (weights 1-11; with a remainder of 10 the weights 3-11, 1, 2 are '
                              'used and a second 10 is invalid)',
        'masks': ('############',)
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate"""
        if not validate_regexp(id_number, IndividualIDNumber.METADATA.regexp):
            return False
        return IndividualIDNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[IINParseResult]:
        """parse the result"""
        match_obj = match_regexp(id_number, IndividualIDNumber.METADATA.regexp)
        if not match_obj:
            return None
        iin_checksum = IndividualIDNumber.checksum(id_number)
        if iin_checksum is None or iin_checksum != int(match_obj.group('checksum')):
            return None
        gender_year_base = IndividualIDNumber.get_gender_year_base(cast(CHECK_DIGIT, int(match_obj.group('century'))))
        if not gender_year_base:
            return None
        gender, year_base = gender_year_base
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        try:
            calendar_date = _calendar_date(yy + year_base, mm, dd)
            if calendar_date is None:
                return None
            return {
                'yyyymmdd': calendar_date,
                'gender': gender,
                'sn': match_obj.group('sn'),
                'checksum': cast(CHECK_DIGIT, int(match_obj.group('checksum'))),
            }
        except ValueError:
            # catch the date error
            return None

    @staticmethod
    def checksum(id_number: str) -> Union[CHECK_DIGIT, Literal[False], None]:
        if not validate_regexp(id_number, IndividualIDNumber.METADATA.regexp):
            return False
        return checksum(id_number)

    @staticmethod
    def get_gender_year_base(century: CHECK_DIGIT) -> Optional[Tuple[Gender, int]]:
        gender = Gender.MALE if century % 2 == 1 else Gender.FEMALE
        if 1 <= century < 3:
            year_base = 1800
        elif 3 <= century < 5:
            year_base = 1900
        elif 5 <= century < 7:
            year_base = 2000
        else:
            return None
        return gender, year_base
