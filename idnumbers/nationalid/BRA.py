import re
from types import SimpleNamespace
from typing import Optional, TypedDict


def normalize(id_number):
    return re.sub(r'[\-/]|[./]', '', id_number)


class ParseResult(TypedDict):
    first_section: str
    second_section: str
    third_section: str
    check_digit: str


class RGNumber:
    """
    Brazil Registro Geral Number
    https://en.wikipedia.org/wiki/National_identification_number#Brazil
    https://learn.microsoft.com/en-us/microsoft-365/compliance/sit-defn-brazil-national-identification-card?view=o365-worldwide
    https://en.wikipedia.org/wiki/Brazilian_identity_card
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BR',
        'min_length': 12,
        'max_length': 12,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<first_section>\d{2})'
                             r'(\.)'
                             r'(?P<second_section>\d{3})'
                             r'(\.)'
                             r'(?P<third_section>\d{3})'
                             r'(-)'
                             r'(?P<check_digit>[\d|X])$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the BRA RegistroGeralNumber
        """
        if not isinstance(id_number, str):
            id_number = repr(id_number)
        elif RGNumber.parse(id_number) is None:
            return False
        return RGNumber.checksum(id_number)

    @staticmethod
    def parse(id_number) -> Optional[ParseResult]:
        match_obj = RGNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        return {k: match_obj.group(k) for k in ['first_section', 'second_section', 'third_section', 'check_digit']}

    MAGIC_MULTIPLIER = [2, 3, 4, 5, 6, 7, 8, 9]

    @staticmethod
    def checksum(id_number: str) -> bool:
        normalized = normalize(id_number)
        number_list = [int(char) for char in list(normalized[:8])]
        # X is equal to 11 in check digit
        check_digit = 11 if normalized[8] == 'X' else int(normalized[8])
        total = sum([value * RGNumber.MAGIC_MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        return True if ((total + check_digit * 100) % 11) == 0 else False


class CPFNumber:
    """
       Brazil CPF number
       https://en.wikipedia.org/wiki/National_identification_number#Brazil
       """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BR',
        'min_length': 14,
        'max_length': 14,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<first_section>\d{3})'
                             r'(\.)'
                             r'(?P<second_section>\d{3})'
                             r'(\.)'
                             r'(?P<third_section>\d{3})'
                             r'(-)'
                             r'(?P<check_digit>\d{2})$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the BRA Cadastro de Pessoas Físicas Number
        https://en.wikipedia.org/wiki/CPF_number
        https://4app.net/tools/validator/document/cpf_validator
        """
        if not isinstance(id_number, str):
            id_number = repr(id_number)
        elif CPFNumber.parse(id_number) is None:
            return False
        return CPFNumber.checksum(id_number)

    @staticmethod
    def parse(id_number) -> Optional[ParseResult]:
        match_obj = CPFNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        return {k: match_obj.group(k) for k in ['first_section', 'second_section', 'third_section', 'check_digit']}

    @staticmethod
    def checksum(id_number: str) -> bool:
        normalized = normalize(id_number)
        number_list = [int(char) for char in list(normalized[:9])]
        return normalized[9] == CPFNumber.first_digit_checksum(number_list) and normalized[
            10] == CPFNumber.second_digit_checksum(number_list)

    FIRST_MAGIC_MULTIPLIER = [10, 9, 8, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def first_digit_checksum(number_list) -> str:
        total = sum([value * CPFNumber.FIRST_MAGIC_MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        return str(CPFNumber.get_checksum(total))

    SECOND_MAGIC_MULTIPLIER = [11, 10, 9, 8, 7, 6, 5, 4, 3]

    @staticmethod
    def second_digit_checksum(number_list) -> str:
        first_checksum = CPFNumber.first_digit_checksum(number_list)
        total = sum([value * CPFNumber.SECOND_MAGIC_MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        # Using first digit of the checksum to get total
        total += int(first_checksum) * 2
        return str(CPFNumber.get_checksum(total))

    @staticmethod
    def get_checksum(total: int) -> int:
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

# TODO RIC NUMBER
