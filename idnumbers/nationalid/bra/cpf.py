import re
from types import SimpleNamespace
from ..util import validate_regexp
from .util import normalize


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
        'regexp': re.compile(r'^(\d{3}\.?\d{3}\.?\d{3}-?\d{2})$'),
        'alias_of': None,
        'names': ['CPF number',
                  'Cadastro de Pessoas Físicas'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Brazil'],
        'deprecated': False
    })

    MULTIPLIER1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    MULTIPLIER2 = [11, 10, 9, 8, 7, 6, 5, 4, 3]

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

        total = sum([value * CPFNumber.MULTIPLIER1[index] for (index, value) in enumerate(number_list)])
        return str(CPFNumber.get_checksum(total))

    @staticmethod
    def second_digit_checksum(number_list) -> str:
        """Get the second checksum digit"""

        first_checksum = CPFNumber.first_digit_checksum(number_list)
        total = sum([value * CPFNumber.MULTIPLIER2[index] for (index, value) in enumerate(number_list)])
        # Using first digit of the checksum to get total
        total += int(first_checksum) * 2
        return str(CPFNumber.get_checksum(total))

    @staticmethod
    def get_checksum(total: int) -> int:
        """Map the total sum to checksum number"""
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
