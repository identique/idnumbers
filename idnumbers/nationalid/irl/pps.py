import re
from ..metadata import IdMetadata
from ..util import validate_regexp, weighted_modulus_digit, letter_to_number


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return id_number.replace('/', '')


class PersonalPublicServiceNumber:
    """
    Ireland Personal Public Service Number

    The current check-character algorithm follows python-stdnum 2.2:
    https://github.com/arthurdejong/python-stdnum/blob/2.2/stdnum/ie/pps.py
    The algorithm recognizes optional suffixes A, B, H, W and space. A, B and
    H contribute to the check-character calculation; W and space are ignored.
    This describes validation behavior and does not claim H is issued to
    individuals. Historical T/X suffix handling is not implemented here and
    is tracked separately: https://github.com/identique/idnumbers/issues/433
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'IE',
        'min_length': 8,
        'max_length': 10,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^\d{7}[A-W][ABHW ]?$|'
                             r'^\d{7}[A-W]/[ABHW ]?$'),
        'alias_of': None,
        'names': ['Personal Public Service Number',
                  'PPS',
                  'Uimhir Phearsanta Seirbhíse Poiblí',
                  'Uimh. PSP',
                  'Revenue and Social Insurance Number',
                  'RSI No'],
        'links': ['https://en.wikipedia.org/wiki/Personal_Public_Service_Number',
                  'https://github.com/arthurdejong/python-stdnum/blob/2.2/stdnum/ie/pps.py'],
        'deprecated': False
    })

    MAGIC_MULTIPLIER = [8, 7, 6, 5, 4, 3, 2, 9]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the IRL personal public service number
        """
        if not validate_regexp(id_number, PersonalPublicServiceNumber.METADATA.regexp):
            return False
        return PersonalPublicServiceNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """algorithm: https://en.wikipedia.org/wiki/Personal_Public_Service_Number#Check_character"""
        normalized = normalize(id_number)
        number_list = [int(i) for i in normalized[:7]]
        if len(normalized) == 9 and normalized[-1] not in [' ', 'W']:
            number_list.append(letter_to_number(normalized[-1]))
        modulus = weighted_modulus_digit(numbers=number_list,
                                         weights=PersonalPublicServiceNumber.MAGIC_MULTIPLIER,
                                         divider=23, modulus_only=True)
        # the last digit is a check_char if the length is 8
        check_char = normalized[-2] if len(normalized) == 9 else normalized[-1]

        return modulus == letter_to_number(check_char) % 23
