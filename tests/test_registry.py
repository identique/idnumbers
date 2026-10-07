"""Tests of the country registry (idnumbers.registry)."""

import importlib
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, List, Optional, Type
from unittest import TestCase, main
from unittest.mock import patch

import idnumbers
from idnumbers import registry
from idnumbers.nationalid import AUS, GRC, TWN

REPO_ROOT = Path(__file__).resolve().parents[1]
NATIONALID_DIR = REPO_ROOT / 'idnumbers' / 'nationalid'
COUNTRY_COUNT = 78
ID_TYPE_COUNT = 104


def make_validator(alpha2: Optional[str] = 'QQ') -> Type[Any]:
    """Build a throwaway ID class like the ones of the library."""

    class Throwaway:
        METADATA = SimpleNamespace(iso3166_alpha2=alpha2)

        @staticmethod
        def validate(id_number: str) -> bool:
            return id_number == 'ok'

    return Throwaway


class TestBuiltinTable(TestCase):
    def test_table_matches_the_country_modules(self) -> None:
        stems = {path.stem for path in NATIONALID_DIR.glob('[A-Z][A-Z][A-Z].py')}
        self.assertEqual(len(stems), COUNTRY_COUNT)
        self.assertEqual(stems, set(registry._BUILTIN))

    def test_every_entry_agrees_with_its_module(self) -> None:
        id_type_total = 0
        names = []
        for alpha3 in sorted(registry._BUILTIN):
            with self.subTest(alpha3=alpha3):
                module = importlib.import_module('idnumbers.nationalid.' + alpha3)
                entry = registry.get_country(alpha3)
                assert entry is not None
                national_id = module.NationalID
                alpha2 = national_id.METADATA.iso3166_alpha2
                self.assertEqual(entry.alpha3, alpha3)
                self.assertEqual(entry.alpha2, alpha2)
                self.assertIs(entry.national_id, national_id)
                self.assertIn(national_id.METADATA.alias_of or national_id, entry.id_types)
                self.assertEqual(len(entry.id_types), len(set(entry.id_types)))
                for id_type in entry.id_types:
                    self.assertTrue(hasattr(id_type, 'METADATA'))
                    self.assertIsNone(id_type.METADATA.alias_of)
                    self.assertEqual(id_type.METADATA.iso3166_alpha2, alpha2)
                self.assertTrue(entry.name)
                names.append(entry.name)
                id_type_total += len(entry.id_types)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(id_type_total, ID_TYPE_COUNT)

    def test_primary_types_are_unchanged(self) -> None:
        aus = registry.get_country('AUS')
        assert aus is not None
        self.assertEqual(aus.id_types, (AUS.DriverLicenseNumber, AUS.MedicareNumber, AUS.TaxFileNumber))
        self.assertIs(registry.get_validator('AUS'), AUS.NationalID)
        self.assertIs(AUS.NationalID.METADATA.alias_of, AUS.DriverLicenseNumber)
        self.assertIs(GRC.NationalID.METADATA.alias_of, GRC.IdentityCard)
        self.assertIs(registry.get_validator('GRC'), GRC.NationalID)
        twn = registry.get_country('TWN')
        assert twn is not None
        self.assertEqual(twn.id_types, (TWN.NationalID,))

    def test_names(self) -> None:
        expected = {
            'TWN': 'Taiwan',
            'KOR': 'South Korea',
            'VNM': 'Vietnam',
            'BIH': 'Bosnia and Herzegovina',
            'HKG': 'Hong Kong',
            'MAC': 'Macao',
            'CZE': 'Czechia',
            'TUR': 'Türkiye',
            'GBR': 'United Kingdom',
            'USA': 'United States',
        }
        for alpha3, name in expected.items():
            with self.subTest(alpha3=alpha3):
                entry = registry.get_country(alpha3)
                assert entry is not None
                self.assertEqual(entry.name, name)


class TestLookup(TestCase):
    def test_accepted_forms(self) -> None:
        for code in ('tw', 'TW', 'tW', 'twn', 'TWN', 'Twn'):
            with self.subTest(code=code):
                self.assertEqual(registry.resolve_country(code), 'TWN')
                entry = registry.get_country(code)
                assert entry is not None
                self.assertEqual((entry.alpha3, entry.alpha2, entry.name), ('TWN', 'TW', 'Taiwan'))
                self.assertIs(registry.get_validator(code), TWN.NationalID)

    def test_unknown_input_gives_none_and_never_raises(self) -> None:
        bad: List[Any] = [
            None, 0, 1, 1.5, b'TW', ['TW'], '', ' ', ' TW', 'TW ', 'TW\n', 'XX', 'TWNX', 'T', 'ın', 'ｔｗ',
        ]
        for value in bad:
            with self.subTest(value=value):
                self.assertIsNone(registry.resolve_country(value))
                self.assertIsNone(registry.get_country(value))
                self.assertIsNone(registry.get_validator(value))

    def test_validator_validates(self) -> None:
        validator = registry.get_validator('TW')
        assert validator is not None
        self.assertIs(validator.validate('A123456789'), True)
        self.assertIs(validator.validate('A123456780'), False)

    def test_package_reexports(self) -> None:
        self.assertIs(idnumbers.get_country, registry.get_country)
        self.assertIs(idnumbers.get_validator, registry.get_validator)
        self.assertIs(idnumbers.resolve_country, registry.resolve_country)
        self.assertIs(idnumbers.list_supported_countries, registry.list_supported_countries)
        self.assertIs(idnumbers.register, registry.register)
        self.assertIs(idnumbers.CountryEntry, registry.CountryEntry)


class TestListSupportedCountries(TestCase):
    def test_lists_all_sorted(self) -> None:
        countries = registry.list_supported_countries()
        self.assertEqual(len(countries), COUNTRY_COUNT)
        alpha3_codes = [entry.alpha3 for entry in countries]
        self.assertEqual(alpha3_codes, sorted(alpha3_codes))
        self.assertEqual(tuple(countries[0][:3]), ('ALB', 'AL', 'Albania'))

    def test_returns_a_new_list(self) -> None:
        first = registry.list_supported_countries()
        first.clear()
        self.assertEqual(len(registry.list_supported_countries()), COUNTRY_COUNT)


class TestLazyImport(TestCase):
    def run_code(self, code: str) -> None:
        env = dict(os.environ, PYTHONPATH=str(REPO_ROOT))
        subprocess.run([sys.executable, '-c', code], cwd=str(REPO_ROOT), env=env, check=True)

    def test_import_does_not_load_country_modules(self) -> None:
        self.run_code("import sys, idnumbers\nassert 'idnumbers.nationalid' not in sys.modules\n")

    def test_lookup_loads_only_that_country(self) -> None:
        self.run_code(
            'import sys, idnumbers\n'
            "assert idnumbers.resolve_country('tw') == 'TWN'\n"
            "assert 'idnumbers.nationalid.TWN' not in sys.modules\n"
            "assert idnumbers.get_validator('tw') is not None\n"
            "assert 'idnumbers.nationalid.TWN' in sys.modules\n"
            "assert 'idnumbers.nationalid.JPN' not in sys.modules\n"
        )


class RegistryStateCase(TestCase):
    """Restores the registry state after each test."""

    def setUp(self) -> None:
        for state in (registry._KEYS, registry._ENTRIES, registry._CUSTOM):
            patcher = patch.dict(state)
            patcher.start()
            self.addCleanup(patcher.stop)

    def snapshot(self) -> Any:
        return dict(registry._KEYS), dict(registry._ENTRIES), dict(registry._CUSTOM)


class TestRegister(RegistryStateCase):
    def test_success_with_all_arguments(self) -> None:
        validator = make_validator('XA')
        registry.register('xyz', validator, alpha2='xy', name='Xanadu', aliases=['xx', 'Legacy'])
        for code in ('xyz', 'XYZ', 'xy', 'XY', 'xx', 'LEGACY', 'legacy'):
            with self.subTest(code=code):
                entry = registry.get_country(code)
                assert entry is not None
                self.assertEqual(entry, registry.CountryEntry('XYZ', 'XY', 'Xanadu', validator, (validator,)))
                self.assertIs(registry.get_validator(code), validator)
        self.assertEqual(registry.resolve_country('legacy'), 'XYZ')
        countries = registry.list_supported_countries()
        self.assertEqual(len(countries), COUNTRY_COUNT + 1)
        self.assertEqual([entry.alpha3 for entry in countries], sorted(entry.alpha3 for entry in countries))
        self.assertIn('XYZ', [entry.alpha3 for entry in countries])

    def test_defaults(self) -> None:
        validator = make_validator('xa')
        registry.register('abc', validator)
        entry = registry.get_country('ABC')
        assert entry is not None
        self.assertEqual((entry.alpha3, entry.alpha2, entry.name), ('ABC', 'XA', 'ABC'))
        self.assertIs(registry.get_validator('xa'), validator)

    def test_idempotent(self) -> None:
        validator = make_validator()
        registry.register('abc', validator, alpha2='ab', name='Abc', aliases=('one', 'two'))
        before = self.snapshot()
        registry.register('ABC', validator, alpha2='AB', name='Abc', aliases=('TWO', 'one'))
        self.assertEqual(self.snapshot(), before)

    def test_builtin_noop(self) -> None:
        before = self.snapshot()
        registry.register('TWN', TWN.NationalID)
        registry.register('twn', TWN.NationalID, alpha2='tw', name='Taiwan')
        self.assertEqual(registry.list_supported_countries()[0].alpha3, 'ALB')
        self.assertEqual(len(registry.list_supported_countries()), COUNTRY_COUNT)
        self.assertEqual(registry._CUSTOM, before[2])

    def test_type_errors(self) -> None:
        validator = make_validator()
        no_metadata = type('NoMetadata', (), {'validate': staticmethod(lambda value: True)})
        no_validate = type('NoValidate', (), {'METADATA': SimpleNamespace(iso3166_alpha2='QQ')})
        bad_validate = type('BadValidate', (), {'METADATA': SimpleNamespace(iso3166_alpha2='QQ'), 'validate': 1})
        cases: List[Any] = [
            (1, validator, {}),
            (None, validator, {}),
            ('abc', 'not a class', {}),
            ('abc', validator(), {}),
            ('abc', no_metadata, {}),
            ('abc', no_validate, {}),
            ('abc', bad_validate, {}),
            ('abc', validator, {'alpha2': 12}),
            ('abc', validator, {'name': 12}),
            ('abc', validator, {'aliases': 'TW'}),
            ('abc', validator, {'aliases': ['ok', 1]}),
            ('abc', validator, {'aliases': [None]}),
        ]
        before = self.snapshot()
        for alpha3, bad_validator, kwargs in cases:
            with self.subTest(alpha3=alpha3, validator=bad_validator, kwargs=kwargs):
                with self.assertRaises(TypeError):
                    registry.register(alpha3, bad_validator, **kwargs)
        self.assertEqual(self.snapshot(), before)

    def test_value_errors(self) -> None:
        validator = make_validator()
        no_alpha2 = make_validator(None)
        digit_alpha2 = make_validator('Q1')
        long_alpha2 = make_validator('QQQ')
        cases: List[Any] = [
            ('ab', validator, {}),
            ('abcd', validator, {}),
            ('', validator, {}),
            ('a1c', validator, {}),
            ('äbc', validator, {}),
            ('abc', no_alpha2, {}),
            ('abc', digit_alpha2, {}),
            ('abc', long_alpha2, {}),
            ('abc', validator, {'alpha2': 'q'}),
            ('abc', validator, {'alpha2': 'qqq'}),
            ('abc', validator, {'alpha2': ''}),
            ('abc', validator, {'alpha2': 'q1'}),
            ('abc', validator, {'name': ''}),
            ('abc', validator, {'aliases': ['']}),
            ('abc', validator, {'aliases': ['ünï']}),
            ('abc', validator, {'aliases': ['a b']}),
            ('abc', validator, {'aliases': ['a\n']}),
            ('abc', validator, {'aliases': ['xx', 'XX']}),
            ('abc', validator, {'aliases': ['qq']}),
            ('abc', validator, {'aliases': ['ABC']}),
            ('abc', validator, {'alpha2': 'ab', 'aliases': ['ab']}),
        ]
        before = self.snapshot()
        for alpha3, bad_validator, kwargs in cases:
            with self.subTest(alpha3=alpha3, validator=bad_validator, kwargs=kwargs):
                with self.assertRaises(ValueError):
                    registry.register(alpha3, bad_validator, **kwargs)
        self.assertEqual(self.snapshot(), before)

    def test_non_ascii_codes_that_uppercase_to_ascii_are_rejected(self) -> None:
        # 'ß'.upper() == 'SS' and 'ﬀ'.upper() == 'FF', so only the original string shows the code isn't ASCII.
        before = self.snapshot()
        for alpha3 in ('ßq', 'ﬀa'):
            with self.subTest(alpha3=alpha3):
                with self.assertRaises(ValueError):
                    registry.register(alpha3, make_validator())
        for alpha2 in ('ß', 'ﬀ', 'ßQ', 'ﬀQ'):
            with self.subTest(alpha2=alpha2):
                with self.assertRaises(ValueError):
                    registry.register('abc', make_validator(), alpha2=alpha2)
                with self.assertRaises(ValueError):
                    registry.register('abc', make_validator(alpha2))
        self.assertEqual(self.snapshot(), before)
        self.assertIsNone(registry.resolve_country('SSQ'))
        self.assertIsNone(registry.resolve_country('FFA'))

    def test_error_messages_name_the_code(self) -> None:
        with self.assertRaisesRegex(ValueError, "'ab'"):
            registry.register('ab', make_validator())
        with self.assertRaisesRegex(ValueError, "'TW'"):
            registry.register('abc', make_validator('TW'))
        with self.assertRaisesRegex(ValueError, 'TWN'):
            registry.register('abc', make_validator(), aliases=['twn'])

    def test_builtin_cannot_be_replaced_or_widened(self) -> None:
        before = self.snapshot()
        with self.assertRaises(ValueError):
            registry.register('TWN', make_validator('TW'))
        with self.assertRaises(ValueError):
            registry.register('TWN', TWN.NationalID, aliases=['formosa'])
        with self.assertRaises(ValueError):
            registry.register('TWN', TWN.NationalID, name='Formosa')
        with self.assertRaises(ValueError):
            registry.register('TWN', TWN.NationalID, alpha2='TX')
        self.assertEqual(self.snapshot(), before)
        self.assertIsNone(registry.resolve_country('formosa'))
        self.assertIs(registry.get_validator('TW'), TWN.NationalID)

    def test_custom_cannot_be_registered_again_differently(self) -> None:
        validator = make_validator()
        registry.register('abc', validator, alpha2='ab', name='Abc', aliases=['one'])
        before = self.snapshot()
        changes: List[Any] = [
            (make_validator(), {'alpha2': 'ab', 'name': 'Abc', 'aliases': ['one']}),
            (validator, {'alpha2': 'ac', 'name': 'Abc', 'aliases': ['one']}),
            (validator, {'alpha2': 'ab', 'name': 'Other', 'aliases': ['one']}),
            (validator, {'alpha2': 'ab', 'name': 'Abc', 'aliases': ['one', 'two']}),
            (validator, {'alpha2': 'ab', 'name': 'Abc', 'aliases': []}),
            (validator, {'alpha2': 'ab', 'aliases': ['one']}),
        ]
        for bad_validator, kwargs in changes:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    registry.register('abc', bad_validator, **kwargs)
        self.assertEqual(self.snapshot(), before)

    def test_keys_taken_by_another_country(self) -> None:
        validator = make_validator()
        registry.register('abc', validator, alpha2='ab', aliases=['legacy'])
        before = self.snapshot()
        cases: List[Any] = [
            {'alpha2': 'TW'},
            {'alpha2': 'AB'},
            {'alpha2': 'xy', 'aliases': ['TWN']},
            {'alpha2': 'xy', 'aliases': ['tw']},
            {'alpha2': 'xy', 'aliases': ['ok', 'abc']},
            {'alpha2': 'xy', 'aliases': ['LEGACY']},
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    registry.register('xyz', validator, **kwargs)
        with self.assertRaises(ValueError):
            registry.register('legacy', validator, alpha2='xy')
        self.assertEqual(self.snapshot(), before)

    def test_failure_on_the_second_alias_changes_nothing(self) -> None:
        before = self.snapshot()
        with self.assertRaises(ValueError):
            registry.register('xyz', make_validator(), alpha2='xy', aliases=['fine', 'tw'])
        self.assertEqual(self.snapshot(), before)
        with self.assertRaises(ValueError):
            registry.register('xyz', make_validator(), alpha2='xy', aliases=['fine', 'has space'])
        self.assertEqual(self.snapshot(), before)
        self.assertIsNone(registry.resolve_country('fine'))
        self.assertIsNone(registry.resolve_country('xyz'))
        self.assertIsNone(registry.resolve_country('xy'))

    def test_state_is_restored_between_tests(self) -> None:
        self.assertEqual(len(registry.list_supported_countries()), COUNTRY_COUNT)
        self.assertIsNone(registry.get_country('abc'))


if __name__ == '__main__':
    main()
