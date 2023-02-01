from re import Pattern
from typing import List, Literal, Optional, Type, cast

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
"""[Table](https://en.wikipedia.org/wiki/Verhoeff_algorithm#Table-based_algorithm) for the Verhoeff algorithm"""

CHECK_DIGIT: Type[int] = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
"""Check digit type. Numeric check digits are only allowed in 0 to 9"""

CHECK_ALPHA = Literal['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                      'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'Y', 'U',
                      'V', 'W', 'X', 'Y', 'Z']
"""Check digit type. Numeric check digits are only allowed in A to Z (all in upper cases)"""


def validate_regexp(id_number: str, regexp: Pattern[str]) -> bool:
    """validate string again the regular expression"""
    assert isinstance(id_number, str), 'id_number MUST be str'
    return regexp.search(id_number) is not None


def luhn_digit(digits: List[int], multipliers_start_by_two: bool = False) -> CHECK_DIGIT:
    """
    implement the algorithm of Luhn.
    https://en.wikipedia.org/wiki/Luhn_algorithm
    :param multipliers_start_by_two: Multipliers start by two
    :param digits: digits for calculating the check digit
    :return: checksum
    """
    total_sum = 0
    for idx, int_val in enumerate([0, *digits] if multipliers_start_by_two else digits):
        if idx % 2 == 0:
            total_sum += int_val
        elif int_val > 4:
            total_sum += (2 * int_val - 9)
        else:
            total_sum += (2 * int_val)
    return cast(CHECK_DIGIT, (10 - total_sum % 10) % 10)


def verhoeff_check(digits: List[int]) -> bool:
    """
    implement the verhoeff algorithm in table format:
    https://en.wikipedia.org/wiki/Verhoeff_algorithm#Table-based_algorithm
    """
    rev_digits = list(digits)
    rev_digits.reverse()
    c = 0
    for idx, num in enumerate(rev_digits):
        p_val = VERHOEFF["P_TABLE"][idx % 8][num]
        c = VERHOEFF["D_TABLE"][c][p_val]
    return c == 0


def weighted_modulus_digit(numbers: List[int], weights: Optional[List[int]], divider: int,
                           modulus_only: bool = False) -> int:
    """
    It metrix-multiples numbers and weights and calculate the modulus by the divider.
    :param numbers: the numbers list.
    :param weights: the weights list which will used in matrix multiplications. If weights is none, we use the
                    [1] * len(numbers) as the weights.
    :param divider: the divider used for calculating modulus.
    :param modulus_only: If True, it returns the modulus calculated by divider,
                         otherwise it returns divider - modulus. The default is False.
    :return: the value
    """
    if weights is None:
        weights = [1] * len(numbers)
    assert len(numbers) <= len(weights), 'numbers length must be less than or equal to weights length'
    modulus = sum([value * weights[index] for (index, value) in enumerate(numbers)]) % divider
    return modulus if modulus_only else divider - modulus


def mn_modulus_digit(numbers: List[int], m: int, n: int) -> int:
    """
    MN modulus check, (official name TBD) ISO 7064 mod 11 (n), 10 (m)?
    1. (adds numbers and product) mod by m
    2. next product = (2 * total) mod by n
    3. return n - product
    :param numbers: numbers
    :param m: M value used by calculate the first step
    :param n: N value used by the 2nd and 3rd step
    :return: the digit
    """
    product = m
    for number in numbers:
        total = (number + product) % m
        if total == 0:
            total = m
        product = (2 * total) % n

    return n - product


def modulus_overflow_mod10(modulus: int) -> CHECK_DIGIT:
    """
    get the units digit of a modulus. Some modulus may not be calculated with 10. In some cases, we need the units digit
    to be the ID.
    """
    return cast(CHECK_DIGIT, modulus % 10 if modulus > 9 else modulus)


def letter_to_number(letter: str, capital: bool = True):
    """
    English letter to its index. A = 1, B = 2...
    """
    assert len(letter) == 1 and letter.isalpha(), 'only allow one alphabet'
    if capital:
        return ord(letter) - 64
    return ord(letter) - 96


def ean13_digit(numbers: List[int]) -> CHECK_DIGIT:
    """
    The EAN-13 validation. The EAN-13 is a [barcode format](https://boxshot.com/barcode/tutorials/ean-13-barcodes/).
    This is the check digit of EAN-13.
    https://boxshot.com/barcode/tutorials/ean-13-calculator/
    """
    odd = 0
    even = 0
    for index, value in enumerate(numbers):
        if (index + 1) % 2 == 0:
            even += value
        else:
            odd += value
    total = even * 2 + odd
    modulus = total % 10
    return cast(CHECK_DIGIT,
                0 if modulus == 0 else (10 - modulus))
