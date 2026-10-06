"""
validate() and parse() are total: they return a bool / None for any input instead of raising.

The tests below feed every ID type
  1. a fixed list of hostile inputs (non-str values, empty and blank strings, very long strings, non-ASCII digits),
  2. a deterministic fuzz: every valid vector found in tests/nationalid/test_*.py, mutated position by position.
"""
import ast
import glob
import os
from typing import Any, Callable, Iterator, List, Set, Tuple
from unittest import TestCase, main

from idnumbers.nationalid import BGR, BRA, CHE, CHL, CZE, EST, GRC, IRN, ISR, JPN, LKA, LVA, NZL, SWE, UKR, ZAF
from tests.test_validate_regexp import _discover_id_types

ARABIC_INDIC_ONE = '١'
FULL_WIDTH_ONE = '１'

NON_STR_INPUTS: List[Any] = [None, 0, 123, 12.5, True, b'123', bytearray(b'1'), [], {}, object()]
STR_INPUTS: List[str] = [
    '', ' ', '\n', '-', 'x' * 1000, '1' * 1000,
    ARABIC_INDIC_ONE * 13, FULL_WIDTH_ONE * 13, ARABIC_INDIC_ONE * 10 + 'A' * 3,
]

FUZZ_SUBSTITUTES = '09AZ- |.²①\n١/'
"""
Substituted at, and inserted before, every position. Besides the plain digit, letter and separator cases it
holds the characters that regexps and checksum code mishandle: '|' and '.' (sloppy character classes),
'²' and '①' (str.isdigit() is True, int() raises), a newline, an Arabic-Indic digit and '/'.
"""
FUZZ_EXTENSIONS = '0A'


def _string_literals() -> Set[str]:
    """Every string literal of tests/nationalid/test_*.py: the real-world vectors, valid and invalid."""
    literals: Set[str] = set()
    pattern = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nationalid', 'test_*.py')
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding='utf-8') as source:
            for node in ast.walk(ast.parse(source.read(), filename=path)):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    literals.add(node.value)
    return literals


def _mutations(vector: str) -> Iterator[str]:
    """Substitute or insert at each position, truncate by 1..n characters, extend with a trailing character."""
    for index in range(len(vector)):
        for char in FUZZ_SUBSTITUTES:
            yield vector[:index] + char + vector[index + 1:]
            yield vector[:index] + char + vector[index:]
    for cut in range(1, len(vector) + 1):
        yield vector[:-cut]
    for char in FUZZ_EXTENSIONS:
        yield vector + char


def _call(method: Callable[[Any], Any], value: Any) -> Tuple[bool, Any]:
    """(raised, result or exception)"""
    try:
        return False, method(value)
    except Exception as error:  # noqa: BLE001 - any exception is the bug under test
        return True, error


def _describe(value: Any) -> str:
    return repr(value) if len(repr(value)) <= 40 else repr(value)[:37] + '...'


class TestEveryIDTypeIsTotal(TestCase):
    def test_non_str_input_is_false_and_never_parsed(self):
        failures: List[str] = []
        for name, cls in _discover_id_types():
            for value in NON_STR_INPUTS:
                raised, result = _call(cls.validate, value)
                if raised or result is not False:
                    failures.append(f'{name}.validate({_describe(value)}) -> {result!r}')
                if getattr(cls.METADATA, 'parsable', False):
                    raised, result = _call(cls.parse, value)
                    if raised or result is not None:
                        failures.append(f'{name}.parse({_describe(value)}) -> {result!r}')
        self.assertEqual([], failures)

    def test_hostile_str_input_is_false_and_never_parsed(self):
        failures: List[str] = []
        for name, cls in _discover_id_types():
            metadata = cls.METADATA
            inputs = list(STR_INPUTS)
            for length in {metadata.min_length, metadata.max_length}:
                if length:
                    inputs += [ARABIC_INDIC_ONE * length, FULL_WIDTH_ONE * length, '\n' * length, ' ' * length]
            for value in inputs:
                raised, result = _call(cls.validate, value)
                if raised or result is not False:
                    failures.append(f'{name}.validate({_describe(value)}) -> {result!r}')
                if getattr(metadata, 'parsable', False):
                    raised, result = _call(cls.parse, value)
                    if raised or result is not None:
                        failures.append(f'{name}.parse({_describe(value)}) -> {result!r}')
        self.assertEqual([], failures)

    def test_fuzzed_valid_vectors_never_raise(self):
        literals = sorted(_string_literals())
        self.assertGreater(len(literals), 300)
        failures: List[str] = []
        checked = 0
        for name, cls in _discover_id_types():
            vectors = [literal for literal in literals if _call(cls.validate, literal) == (False, True)]
            candidates: Set[str] = set(vectors)
            for vector in vectors:
                candidates.update(_mutations(vector))
            parsable = getattr(cls.METADATA, 'parsable', False)
            for value in sorted(candidates):
                checked += 1
                raised, result = _call(cls.validate, value)
                if raised or not isinstance(result, bool):
                    failures.append(f'{name}.validate({_describe(value)}) -> {result!r}')
                if parsable:
                    raised, result = _call(cls.parse, value)
                    if raised:
                        failures.append(f'{name}.parse({_describe(value)}) raised {result!r}')
        self.assertGreater(checked, 10000)
        self.assertEqual([], failures)


class TestIssue278Regressions(TestCase):
    """The examples of issue #278, checked against both libraries when it was filed."""

    def test_none_and_non_str_input(self):
        self.assertIs(False, ZAF.NationalID.validate(None))  # was ValueError through repr(None)
        self.assertIs(False, CZE.TaxNumber.validate(None))  # was TypeError from re.sub
        self.assertIs(False, CZE.TaxNumber.validate(12345))
        self.assertIs(False, EST.NationalID.validate(37605030299))  # an int used to be repr()ed and accepted
        self.assertIs(False, GRC.TaxIdentityNumber.validate(None))
        self.assertIs(False, LVA.PersonalCode.validate(None))
        self.assertIs(False, ISR.NationalID.validate(123456789))
        self.assertIs(False, LKA.NationalID.validate(None))
        self.assertIsNone(ZAF.NationalID.parse(None))

    def test_empty_string(self):
        self.assertIs(False, GRC.TaxIdentityNumber.validate(''))  # was IndexError
        self.assertIs(False, ISR.NationalID.validate(''))  # was IndexError
        self.assertIs(False, LVA.PersonalCode.validate(''))  # was IndexError
        self.assertIs(False, NZL.NationalHealthIndexNumber.validate(''))  # was IndexError (empty alternative)
        self.assertIsNone(NZL.NationalHealthIndexNumber.METADATA.regexp.match(''))

    def test_newline(self):
        self.assertIs(False, GRC.TaxIdentityNumber.validate('094014250\n'))  # was ValueError
        self.assertIs(False, LKA.NationalID.validate('199001200001\n'))  # was ValueError
        self.assertIs(False, NZL.NationalHealthIndexNumber.validate('\n'))  # was ValueError

    def test_non_ascii_digits(self):
        self.assertIs(False, LVA.PersonalCode.validate('١61175-19997'))  # was True

    def test_lka_year_one_overflow(self):
        self.assertIs(False, LKA.NationalID.validate('000100000017'))  # was OverflowError
        self.assertIsNone(LKA.NationalID.parse('000100000017'))

    def test_bgr_parse_and_checksum_on_malformed_input(self):
        self.assertIsNone(BGR.UniformCivilNumber.parse('abc'))  # was AttributeError
        self.assertIsNone(BGR.UniformCivilNumber.checksum('abc'))  # was ValueError
        self.assertIsNone(BGR.UniformCivilNumber.parse(None))
        self.assertIsNone(BGR.UniformCivilNumber.checksum(None))

    def test_bra_checksum_on_malformed_input(self):
        for value in ('abc', '12345', '', None):
            self.assertIs(False, BRA.CPFNumber.checksum(value))  # was ValueError / IndexError
            self.assertIs(False, BRA.RGNumber.checksum(value))

    def test_bra_rg_check_digit_pipe(self):
        # the RG regexp rejects '|' in the check digit position (since #370); end-to-end check, it used to raise
        self.assertIs(False, BRA.RGNumber.validate('12.345.678-|'))

    def test_irn_jpn_checksum_on_non_digit_input(self):
        for value in ('abc', '12345', '', None):
            self.assertIsNone(IRN.NationalID.checksum(value))  # was ValueError
            self.assertIsNone(JPN.MyNumber.checksum(value))  # was ValueError

    def test_chl_checksum_on_malformed_input(self):
        for value in ('abc', '12345', '', None, 123, '10.000.013-K\n'):
            self.assertIsNone(CHL.NationalID.checksum(value))  # was ValueError / TypeError, or a meaningless character

    def test_ukr_parse_on_malformed_input(self):
        for value in ('abc', '12345', '', None):
            self.assertIsNone(UKR.TaxpayerIDNumber.parse(value))
            self.assertIsNone(UKR.TaxpayerIDNumber.checksum(value))

    def test_che_separator_is_not_a_digit(self):
        # found by the fuzz: the regexp had an unescaped '.' before the last two digits, any character got through
        self.assertIs(False, CHE.SocialSecurityNumber.validate('756.1234.5678-97'))  # was ValueError
        self.assertIs(False, CHE.SocialSecurityNumber.validate('756.1234.5678 97'))

    def test_che_non_ascii_digit_like_separator(self):
        # str.isdigit() is True for these, int() raised ValueError for them: the regexp now rejects them
        for value in ('756.1234.5678²97', '756.1234.5678³97', '756.1234.5678①97'):
            self.assertIs(False, CHE.SocialSecurityNumber.validate(value), value)

    def test_swe_pipe_separator_is_invalid(self):
        # the separator class [+-] rejects '|' (since #370); end-to-end check, it used to raise ValueError
        self.assertIs(False, SWE.PersonalIdentityNumber.validate('191231|2392'))
        self.assertIsNone(SWE.PersonalIdentityNumber.parse('850709|9805'))
        self.assertIsNone(SWE.PersonalIdentityNumber.checksum('850709|9805'))

    def test_swe_plus_and_minus_vectors_are_unchanged(self):
        # vectors from tests/nationalid/test_SWE.py
        self.assertTrue(SWE.PersonalIdentityNumber.validate('850709-9805'))
        self.assertTrue(SWE.PersonalIdentityNumber.validate('191231+2392'))
        self.assertFalse(SWE.PersonalIdentityNumber.validate('850709-9802'))
        self.assertFalse(SWE.PersonalIdentityNumber.validate('191231+2391'))
        self.assertEqual(5, SWE.PersonalIdentityNumber.checksum('850709-9805'))
        self.assertEqual((1985, 7, 9), SWE.PersonalIdentityNumber.parse('850709-9805')['yyyymmdd'].timetuple()[:3])
        self.assertEqual('5', SWE.PersonalIdentityNumber.parse('850709-9805')['checksum'])

    def test_valid_ids_are_still_valid(self):
        self.assertTrue(GRC.TaxIdentityNumber.validate('094014250'))
        self.assertTrue(LVA.PersonalCode.validate('290156-11605'))
        self.assertTrue(CHE.SocialSecurityNumber.validate('756.1234.5678.97'))
        self.assertTrue(NZL.NationalHealthIndexNumber.validate('ZAA0008'))


if __name__ == '__main__':
    main()
