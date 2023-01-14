import re
from types import SimpleNamespace
from .util import validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[\-/]|[./]', '', id_number)


class RGNumber:
    """
    Brazil Registro Geral Number
    https://en.wikipedia.org/wiki/National_identification_number#Brazil
    https://en.wikipedia.org/wiki/Brazilian_identity_card
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BR',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^(\d{2}[.]\d{3}[.]\d{3}[-][\d|X])$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the BRA RegistroGeralNumber
        """
        if not validate_regexp(id_number, RGNumber.METADATA.regexp):
            return False
        return RGNumber.checksum(id_number)

    MAGIC_MULTIPLIER = [2, 3, 4, 5, 6, 7, 8, 9]

    @staticmethod
    def checksum(id_number: str) -> bool:
        """Validate RG number checksum"""
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
        # length without insignificant chars
        'min_length': 11,
        'max_length': 11,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^(\d{3}[.]\d{3}[.]\d{3}[-]\d{2})$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the BRA Cadastro de Pessoas Físicas Number
        https://en.wikipedia.org/wiki/CPF_number
        https://4app.net/tools/validator/document/cpf_validator
        """
        if not validate_regexp(id_number, CPFNumber.METADATA.regexp):
            return False
        return CPFNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """Validate CPF number checksum digits"""
        normalized = normalize(id_number)
        number_list = [int(char) for char in list(normalized[:9])]
        return normalized[9] == CPFNumber.first_digit_checksum(number_list) and normalized[
            10] == CPFNumber.second_digit_checksum(number_list)

    @staticmethod
    def first_digit_checksum(number_list) -> str:
        """Get the first checksum digit"""
        MULTIPLIER = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        total = sum([value * MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        return str(CPFNumber.get_checksum(total))

    @staticmethod
    def second_digit_checksum(number_list) -> str:
        """Get the second checksum digit"""
        MULTIPLIER = [11, 10, 9, 8, 7, 6, 5, 4, 3]
        first_checksum = CPFNumber.first_digit_checksum(number_list)
        total = sum([value * MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        # Using first digit of the checksum to get total
        total += int(first_checksum) * 2
        return str(CPFNumber.get_checksum(total))

    @staticmethod
    def get_checksum(total: int) -> int:
        """Map the total sum to checksum number"""
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
