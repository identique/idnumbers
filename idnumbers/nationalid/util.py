import re
from copy import copy
from functools import lru_cache
from re import Match, Pattern
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


@lru_cache(maxsize=256)
def _ascii_pattern(regexp: Pattern) -> Pattern:
    """
    Build the ASCII-only twin of a compiled pattern.

    A ``str`` pattern is compiled with ``re.UNICODE`` implicitly, and that flag cannot be combined
    with ``re.ASCII``, so it is removed first. Every other flag, such as ``re.IGNORECASE``, is kept.
    A ``bytes`` pattern is ASCII-only already and is returned untouched.
    """
    if isinstance(regexp.pattern, bytes):
        return regexp
    return re.compile(regexp.pattern, (regexp.flags & ~re.UNICODE) | re.ASCII)


def match_regexp(id_number: str, regexp: Pattern[str]) -> Optional[Match[str]]:
    """
    Match the whole id number against the regular expression, in ASCII mode.

    Python's ``re`` module has two traps that let malformed input through a pattern such as
    ``^\\d{3}$`` (see https://docs.python.org/3/library/re.html):

      - ``$`` matches at the end of the string *and just before a trailing newline*, so ``"123\\n"``
        matches. ``Pattern.fullmatch`` only succeeds when the whole string is consumed.
      - ``\\d`` (and ``\\w``, ``\\s``) on a ``str`` pattern match any Unicode decimal digit, such as
        Arabic-Indic or full-width digits, unless ``re.ASCII`` is set. Those later crash ``int()``
        based checksum code.

    The compiled ``METADATA.regexp`` objects are left unchanged (``tools.collect_regexp`` dumps
    them); the ASCII twin is built here and cached.

    Input that is not a ``str`` (``None``, numbers, ``bytes``, lists, ...) never matches. It is not an
    error: validators must return False for it instead of raising, and no ``assert`` is used because
    asserts are stripped under ``python -O``.

    :param id_number: the id number; any non-str value gives None
    :param regexp: compiled pattern, expected to describe the whole id number
    :return: the match object (named groups are preserved), or None when the input is not a str or does not match
    """
    if not isinstance(id_number, str):
        return None
    return _ascii_pattern(regexp).fullmatch(id_number)


def validate_regexp(id_number: str, regexp: Pattern[str]) -> bool:
    """
    Validate that the whole string matches the regular expression, using ASCII digits only.

    A trailing newline and non-ASCII digits are rejected, see :func:`match_regexp` for the reasons.
    Input that is not a ``str`` is rejected too: the result is False, it never raises.
    """
    return match_regexp(id_number, regexp) is not None


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
    :param modulus_only: If True, it returns the modulus calculated by divider, otherwise it returns divider - modulus.
    The default is False.
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
    This is the check digit of EAN-13: the 12 data digits are weighted 1, 3, 1, 3, ... from the left (the odd
    positions by 1, the even positions by 3), and the check digit completes the weighted sum to a multiple of 10.
    https://www.gs1.org/services/how-calculate-check-digit-manually
    https://boxshot.com/barcode/tutorials/ean-13-calculator/
    """
    odd = 0
    even = 0
    for index, value in enumerate(numbers):
        if (index + 1) % 2 == 0:
            even += value
        else:
            odd += value
    total = even * 3 + odd
    modulus = total % 10
    return cast(CHECK_DIGIT,
                0 if modulus == 0 else (10 - modulus))


def alias_of(cls: Type) -> Type:
    assert hasattr(cls, 'METADATA'), f'the type {cls} must have METADATA attribute'
    metadata = copy(cls.METADATA)
    metadata.alias_of = cls

    class AliasType(cls):
        METADATA = metadata

    return AliasType
