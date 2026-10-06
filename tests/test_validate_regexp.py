import importlib
import inspect
import pkgutil
import re
from typing import Dict, List, Tuple, Type
from unittest import TestCase, main

import idnumbers.nationalid as nationalid_package
from idnumbers.nationalid import CHN, DEU, ESP, FRA, IND, IRL, ITA, KOR, MEX, NLD, POL, SWE, TWN, USA
from idnumbers.nationalid.util import match_regexp, validate_regexp

ARABIC_INDIC_ONE = '١'
FULL_WIDTH_ONE = '１'
MAX_SWEEP_LENGTH = 40
"""upper bound of the swept lengths, for the types that do not declare a max_length"""

SWEEP_EXCLUSIONS: Dict[str, str] = {}
"""
ID type classes (as `module.ClassName`) that are skipped by the sweep, with the reason.
It is empty on purpose: every type is checked. If a type must be added, document why and which
issue tracks the real fix, never drop it silently.
"""


class TestValidateRegexp(TestCase):
    def test_valid_ascii_input_matches(self):
        pattern = re.compile(r'^\d{3}$')
        self.assertTrue(validate_regexp('123', pattern))

    def test_invalid_ascii_input_does_not_match(self):
        pattern = re.compile(r'^\d{3}$')
        self.assertFalse(validate_regexp('12', pattern))
        self.assertFalse(validate_regexp('1234', pattern))
        self.assertFalse(validate_regexp('12a', pattern))
        self.assertFalse(validate_regexp('', pattern))

    def test_trailing_newline_is_rejected(self):
        pattern = re.compile(r'^\d{3}$')
        self.assertFalse(validate_regexp('123\n', pattern))
        self.assertFalse(validate_regexp('12\n', pattern))

    def test_leading_newline_is_rejected(self):
        self.assertFalse(validate_regexp('\n123', re.compile(r'^\d{3}$')))

    def test_non_ascii_digits_are_rejected(self):
        pattern = re.compile(r'^\d{3}$')
        self.assertFalse(validate_regexp('١٢٣', pattern))  # Arabic-Indic
        self.assertFalse(validate_regexp('１２３', pattern))  # full-width
        self.assertFalse(validate_regexp('12٣', pattern))  # mixed

    def test_pattern_without_anchors_must_match_the_whole_input(self):
        pattern = re.compile(r'\d{3}')
        self.assertTrue(validate_regexp('123', pattern))
        self.assertFalse(validate_regexp('1234', pattern))
        self.assertFalse(validate_regexp('x123', pattern))

    def test_flags_are_preserved(self):
        pattern = re.compile(r'^[a-z]{2}\d{2}$', re.IGNORECASE)
        self.assertTrue(validate_regexp('Ab12', pattern))
        self.assertFalse(validate_regexp('Ab12\n', pattern))
        self.assertFalse(validate_regexp('Ab١12', pattern))

    def test_literal_non_ascii_characters_still_match(self):
        # the Greek identity cards list Greek capital letters in a character class
        pattern = re.compile(r'^[ΑΒ]-?\d{6}$')
        self.assertTrue(validate_regexp('Α-123456', pattern))
        self.assertFalse(validate_regexp('Α-١٢٣٤٥٦', pattern))

    def test_original_pattern_is_not_modified(self):
        pattern = re.compile(r'^\d{3}$')
        flags = pattern.flags
        validate_regexp('123', pattern)
        self.assertEqual(flags, pattern.flags)
        self.assertEqual(r'^\d{3}$', pattern.pattern)
        # the pattern itself still has the Unicode semantic, only the helper is strict
        self.assertIsNotNone(pattern.search('١٢٣'))

    def test_bytes_pattern_is_left_unchanged(self):
        # a str id number can never match a bytes pattern; the helper must not mask that with a rewrite
        with self.assertRaises(TypeError):
            validate_regexp('123', re.compile(rb'^\d{3}$'))

    def test_match_regexp_keeps_named_groups(self):
        pattern = re.compile(r'^(?P<year>\d{2})(?P<serial>\d{3})$')
        match_obj = match_regexp('12345', pattern)
        self.assertIsNotNone(match_obj)
        self.assertEqual('12', match_obj.group('year'))
        self.assertEqual('345', match_obj.group('serial'))
        self.assertIsNone(match_regexp('12345\n', pattern))

    def test_non_str_never_matches(self):
        pattern = re.compile(r'^\d{3}$')
        for value in (123, None, b'123', bytearray(b'123'), ['1', '2', '3'], 12.5, {}, object()):
            self.assertIs(False, validate_regexp(value, pattern))
            self.assertIsNone(match_regexp(value, pattern))


def _discover_id_types() -> List[Tuple[str, Type]]:
    """
    Find every ID type class: the classes defined in the `idnumbers.nationalid.<iso3>` packages (and in
    shared modules such as `yugoslavia`) that have both `validate` and `METADATA.regexp`.
    The `alias_of` copies live in the upper case `<ISO3>` modules and are not walked again here.
    """
    found: Dict[Type, str] = {}
    for module_info in pkgutil.walk_packages(nationalid_package.__path__, nationalid_package.__name__ + '.'):
        module = importlib.import_module(module_info.name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            metadata = getattr(cls, 'METADATA', None)
            if metadata is None or not hasattr(metadata, 'regexp') or not hasattr(cls, 'validate'):
                continue
            if cls.__module__ != module.__name__ or getattr(metadata, 'alias_of', None) is not None:
                continue
            found.setdefault(cls, f'{cls.__module__}.{cls.__name__}')
    return sorted(((name, cls) for cls, name in found.items()), key=lambda item: item[0])


class TestEveryIDTypeRejectsMalformedInput(TestCase):
    """
    A trailing newline and non-ASCII digits used to pass the format check (`$` matches before a final
    newline, `\\d` matches any Unicode digit) and the checksum code then crashed in int() or returned True.
    """

    def test_id_types_are_discovered(self):
        names = [name for name, _ in _discover_id_types()]
        self.assertGreater(len(names), 90)
        self.assertIn('idnumbers.nationalid.chn.resident_id.ResidentID', names)
        self.assertIn('idnumbers.nationalid.yugoslavia.UniqueMasterCitizenNumber', names)

    def test_malformed_input_is_rejected_without_raising(self):
        failures: List[str] = []
        for name, cls in _discover_id_types():
            if name in SWEEP_EXCLUSIONS:
                continue
            metadata = cls.METADATA
            min_length = metadata.min_length or 1
            max_length = min(metadata.max_length or min_length, MAX_SWEEP_LENGTH)
            for length in range(min_length, max(min_length, max_length) + 1):
                candidates = {
                    'newline after digits': '1' * length + '\n',
                    'newline as last character': '1' * (length - 1) + '\n',
                    'Arabic-Indic digits': ARABIC_INDIC_ONE * length,
                    'full-width digits': FULL_WIDTH_ONE * length,
                }
                for label, candidate in candidates.items():
                    try:
                        result = cls.validate(candidate)
                    except Exception as error:  # noqa: BLE001 - any exception is the bug under test
                        failures.append(f'{name} [{label}, length {length}] raised {error!r}')
                        continue
                    if result is not False:
                        failures.append(f'{name} [{label}, length {length}] returned {result!r}')
        self.assertEqual([], failures)

    def test_exclusions_are_known_types(self):
        names = {name for name, _ in _discover_id_types()}
        self.assertTrue(set(SWEEP_EXCLUSIONS).issubset(names))


class TestKnownGoodVectorsRejectTrailingNewline(TestCase):
    # Each vector is a valid id taken from the first `assertTrue(...validate(...))` of the matching
    # tests/nationalid/test_<ISO3>.py, so it is accepted on its own and rejected once "\n" is appended.
    VECTORS = [
        (CHN.ResidentID, '11010219840406970X'),  # tests/nationalid/test_CHN.py
        (TWN.NationalID, 'A123456789'),  # tests/nationalid/test_TWN.py
        (POL.PESEL, '81010200141'),  # tests/nationalid/test_POL.py
        (SWE.PersonalIdentityNumber, '850709-9805'),  # tests/nationalid/test_SWE.py
        (KOR.NationalID, '820701-2409184'),  # tests/nationalid/test_KOR.py
        (FRA.NationalID, '255081416802538'),  # tests/nationalid/test_FRA.py
        (ESP.NationalID, '12345678Z'),  # tests/nationalid/test_ESP.py
        (ITA.FiscalCode, 'MRTMTT91D08F205J'),  # tests/nationalid/test_ITA.py
        (IND.NationalID, '8924 7352 8038'),  # tests/nationalid/test_IND.py
        (USA.SocialSecurityNumber, '012-12-0928'),  # tests/nationalid/test_USA.py
        (DEU.TaxID, '65929970489'),  # tests/nationalid/test_DEU.py
        (NLD.NationalID, '1234.56.782'),  # tests/nationalid/test_NLD.py
        (MEX.NationalID, 'HEGG560427MVZRRL04'),  # tests/nationalid/test_MEX.py
        (IRL.PersonalPublicServiceNumber, '1234567T'),  # tests/nationalid/test_IRL.py (3rd assertTrue)
    ]

    def test_vector_is_valid_and_newline_variant_is_not(self):
        for cls, vector in self.VECTORS:
            with self.subTest(id_type=f'{cls.METADATA.iso3166_alpha2}.{cls.__qualname__}', vector=vector):
                self.assertTrue(cls.validate(vector))
                self.assertFalse(cls.validate(vector + '\n'))
                self.assertFalse(cls.validate('\n' + vector))

    def test_parse_does_not_accept_the_newline_variant(self):
        for cls, vector in self.VECTORS:
            if not getattr(cls.METADATA, 'parsable', False):
                continue
            with self.subTest(id_type=f'{cls.METADATA.iso3166_alpha2}.{cls.__qualname__}', vector=vector):
                self.assertIsNotNone(cls.parse(vector))
                self.assertIsNone(cls.parse(vector + '\n'))


class TestIRLTrailingWhitespace(TestCase):
    """
    The IRL pattern has an optional trailing character class. It used to be `[A-W\\s]`, and `\\s` matches
    "\\n" and "\\t" (also under re.ASCII), so a trailing newline passed the format check and the checksum
    code then raised. Only a plain space is allowed there now (the old format, see test_IRL.py).
    The sweep above cannot see this, because it only feeds digits.
    """
    PPS = IRL.PersonalPublicServiceNumber

    def test_trailing_space_is_still_valid(self):
        self.assertTrue(self.PPS.validate('1234567T '))  # tests/nationalid/test_IRL.py
        self.assertTrue(self.PPS.validate('1234567TW'))
        self.assertTrue(self.PPS.validate('1234567F/A'))
        self.assertTrue(self.PPS.validate('1234567FA'))

    def test_trailing_newline_tab_and_other_whitespace_are_rejected(self):
        for candidate in ('1234567T\n', '1234567T\t', '1234567T\r', '1234567T\x0b', '1234567T\x0c',
                          '1234567TW\n', '1234567T \n', '1234567T\n\n', '1234567F/A\n', '1234567F/\n',
                          '1234567F/\t', '1234567T\u00a0', '1234567T\u2003'):
            with self.subTest(candidate=candidate):
                self.assertFalse(self.PPS.validate(candidate))

    def test_checksum_with_trailing_space(self):
        self.assertTrue(self.PPS.checksum('1234567T '))
        self.assertTrue(self.PPS.checksum('1234567F/A'))


if __name__ == '__main__':
    main()
