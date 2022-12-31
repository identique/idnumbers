from re import Pattern
from typing import List, Literal, cast

VERHOEFF = {
    'D_TABLE': [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ],

    'P_TABLE': [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]
}


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


def verhoeff_check(digits: List[int]) -> bool:
    rev_digits = list(digits)
    rev_digits.reverse()
    c = 0
    for idx, num in enumerate(rev_digits):
        p_val = VERHOEFF["P_TABLE"][idx % 8][num]
        c = VERHOEFF["D_TABLE"][c][p_val]
    return c == 0


def modulus_check(numbers: List[int], weights: List[int], divider: int, modulus_only: bool = False) -> int:
    assert len(numbers) <= len(weights), 'numbers length must be less than or equal to weights length'
    modulus = sum([value * weights[index] for (index, value) in enumerate(numbers)]) % divider
    return modulus if modulus_only else divider - modulus


def modulus_overflow_mod10(modulus: int) -> Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
    return cast(Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], modulus % 10 if modulus > 9 else modulus)


def letter_to_number(letter: str, capital: bool = True):
    assert len(letter) == 1 and letter.isalpha(), 'only allow one alphabet'
    if capital:
        return ord(letter) - 64
    return ord(letter) - 96
