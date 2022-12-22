from re import Pattern
from typing import List, Literal, cast


def validate_regexp(id_number: str, regexp: Pattern[str]) -> bool:
    assert isinstance(id_number, str), 'id_number MUST be str'
    return regexp.search(id_number) is not None


def luhn_digit(digits: List[int]) -> Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
    """
    implement the algorithm of Luhn.
    https://en.wikipedia.org/wiki/Luhn_algorithm
    :param digits:List[int]
    :return: checksum number
    """
    total_sum = 0
    for idx, int_val in enumerate(digits):
        if idx % 2 == 0:
            total_sum += int_val
        elif int_val > 4:
            total_sum += (2 * int_val - 9)
        else:
            total_sum += (2 * int_val)
    return cast(Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], (10 - total_sum % 10) % 10)
