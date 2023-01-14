import re
from types import SimpleNamespace
from .util import validate_regexp, weighted_modulus_digit, letter_to_number


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return id_number.replace('/', '')


class PersonalPublicServiceNumber:
    """
    Ireland Personal Public Service Number
    https://en.wikipedia.org/wiki/Personal_Public_Service_Number
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'IE',
        'min_length': 8,
        'max_length': 10,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^\d{7}[A-W][A-W\s]?$|'
                             r'^\d{7}[A-W]/[A-W\s]?$')
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
