import re
from types import SimpleNamespace
from ..util import validate_regexp, weighted_modulus_digit


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[-.]', '', id_number)


class NationalID:
    """
    CHL national ID number format, RUN (Rol Único Nacional), RUT (Rol Único Tributario)
    https://en.wikipedia.org/wiki/National_identification_number#Chile
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'CL',
        # length without insignificant chars
        'min_length': 8,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{1,2}\.\d{3}\.\d{3}-[\d|K])$'),
        'alias_of': None,
        'names': ['Rol Único Nacional',
                  'RUN',
                  'Rol Único Tributario',
                  'RUT'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Chile',
                  'https://es.wikipedia.org/wiki/Rol_%C3%9Anico_Tributario#Algoritmo',
                  'https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/cl/rut.py'],
        'deprecated': False
    })

    # The weights are applied to the digits of the body counted from the RIGHT and cycle: 2, 3, 4, 5, 6, 7, 2, 3, ...
    MULTIPLIER = [2, 3, 4, 5, 6, 7]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the CHL id number
        https://codepen.io/alisteroz/pen/KEoqgQ
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.checksum(id_number) == id_number[-1]

    @staticmethod
    def checksum(id_number: str) -> str:
        """
        Calculate the CHL national id number check character (modulo 11).

        The digits of the body (the id without its check character) are weighted from the right with the
        repeating cycle 2, 3, 4, 5, 6, 7, 2, 3, ... so it works for both 7 and 8 digit bodies. The check
        character is 11 - (sum mod 11), where 11 is written as 0 and 10 as K.
        https://es.wikipedia.org/wiki/Rol_%C3%9Anico_Tributario#Algoritmo
        https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/cl/rut.py
        """
        number_list = [int(char) for char in reversed(normalize(id_number)[:-1])]
        weights = [NationalID.MULTIPLIER[index % len(NationalID.MULTIPLIER)] for index in range(len(number_list))]
        modulus = weighted_modulus_digit(number_list, weights, 11)
        return str(0 if modulus == 11 else 'K' if modulus == 10 else modulus)
