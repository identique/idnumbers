

from enum import Enum
from typing import Optional
from ..util import CHECK_DIGIT, weighted_modulus_digit


class EntityType(Enum):
    """Kazakhstan BIN entity type"""
    ResidentEntity = 'resident_entity'
    NonResidentEntity = 'non_resident_entity'
    IP = 'ip'


class EntityDivision(Enum):
    """Kazakhstan BIN entity division type"""
    HeadUnit = 'head_unit'
    Branch = 'branch'
    Representative = 'representative_office'
    Peasant = 'peasant'


WEIGHTS1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
WEIGHTS2 = [3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 2]


def checksum(id_number) -> Optional[CHECK_DIGIT]:
    """
    check the checksum
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Kazakhstan-TIN.pdf
    """
    numbers = [int(char) for char in id_number]
    modulus = weighted_modulus_digit(numbers[0:-1], WEIGHTS1, 11, True)
    if modulus == 10:
        modulus = weighted_modulus_digit(numbers[0:-1], WEIGHTS2, 11, True)
        # the second modulus will not be 10. If it is, it's wrong id number
    return modulus if modulus < 10 else None
