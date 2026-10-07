"""Tests of the unified validation entry point (idnumbers.api)."""

import dataclasses
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Iterator, Optional
from unittest import TestCase, main
from unittest.mock import patch

import idnumbers
from idnumbers import api, registry
from idnumbers.nationalid.constant import Gender
from idnumbers.nationalid import TWN, USA
from tests.parity.corpus import expand_corpus, load_corpus

REPO_ROOT = Path(__file__).resolve().parents[1]
TWN_VALID = 'A123456789'
TWN_INVALID = 'A123456780'
USA_VALID = '012-12-0928'  # Existing regression vector of tests/nationalid/test_USA.py.


@contextmanager
def isolated_registry() -> Iterator[None]:
    """Let a test register a country without changing the registry of the other tests."""
    with patch.dict(registry._KEYS), patch.dict(registry._ENTRIES), patch.dict(registry._CUSTOM):
        yield


class RaisingValidator:
    METADATA = SimpleNamespace(iso3166_alpha2='QQ')

    @staticmethod
    def validate(id_number: str) -> bool:
        raise RuntimeError('boom ' + str(id_number))


class RaisingParser:
    METADATA = SimpleNamespace(iso3166_alpha2='QQ')

    @staticmethod
    def validate(id_number: str) -> bool:
        return True

    @staticmethod
    def parse(id_number: str) -> Dict[str, Any]:
        raise ValueError('cannot parse')


class NoneParser:
    METADATA = SimpleNamespace(iso3166_alpha2='QQ')

    @staticmethod
    def validate(id_number: str) -> bool:
        return True

    @staticmethod
    def parse(id_number: str) -> Optional[Dict[str, Any]]:
        return None


class TestValidate(TestCase):
    def test_every_lookup_form(self) -> None:
        for country in ('tw', 'TW', 'twn', 'TWN'):
            with self.subTest(country=country):
                valid = api.validate(country, TWN_VALID)
                self.assertTrue(valid.is_valid)
                self.assertEqual(valid.country_code, 'TWN')
                self.assertEqual(valid.id_number, TWN_VALID)
                invalid = api.validate(country, TWN_INVALID)
                self.assertFalse(invalid.is_valid)
                self.assertEqual(invalid.country_code, 'TWN')
                self.assertEqual(invalid.reason, api.FailureReason.CHECKSUM_MISMATCH)
                self.assertIsNone(invalid.error_message)
                self.assertIsNone(invalid.extracted_info)

    def test_extracted_info_is_the_parse_result(self) -> None:
        result = api.validate('tw', TWN_VALID)
        self.assertEqual(result.extracted_info, TWN.NationalID.parse(TWN_VALID))
        assert result.extracted_info is not None
        self.assertEqual(result.extracted_info['gender'], Gender.MALE)
        self.assertIsNone(result.reason)
        self.assertIsNone(result.error_message)

    def test_extracted_info_is_a_new_dict_each_call(self) -> None:
        first = api.validate('tw', TWN_VALID)
        assert isinstance(first.extracted_info, dict)
        first.extracted_info['sn'] = 'changed'
        second = api.validate('tw', TWN_VALID)
        assert second.extracted_info is not None
        self.assertIsNot(first.extracted_info, second.extracted_info)
        self.assertEqual(second.extracted_info['sn'], '2345678')

    def test_valid_id_of_a_type_without_parse(self) -> None:
        self.assertFalse(callable(getattr(USA.NationalID, 'parse', None)))
        result = api.validate('us', USA_VALID)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.country_code, 'USA')
        self.assertIsNone(result.extracted_info)
        self.assertIsNone(result.reason)

    def test_unsupported_countries(self) -> None:
        for country in ('XX', '', ' tw', 'ın', None, 1, b'TW', object()):
            with self.subTest(country=repr(country)):
                result = api.validate(country, TWN_VALID)  # type: ignore[arg-type]
                self.assertFalse(result.is_valid)
                self.assertIsNone(result.country_code)
                self.assertEqual(result.reason, api.FailureReason.UNSUPPORTED_COUNTRY)
                assert result.error_message is not None
                self.assertIn(repr(country), result.error_message)
                self.assertIsNone(result.extracted_info)
                self.assertEqual(result.id_number, TWN_VALID)

    def test_id_number_that_is_not_a_string(self) -> None:
        for id_number in (None, 123, b'A123456789'):
            with self.subTest(id_number=repr(id_number)):
                result = api.validate('tw', id_number)  # type: ignore[arg-type]
                self.assertFalse(result.is_valid)
                self.assertEqual(result.country_code, 'TWN')
                self.assertEqual(result.reason, api.FailureReason.INVALID_FORMAT)
                self.assertIsNone(result.extracted_info)
                self.assertIs(result.id_number, id_number)

    def test_id_number_is_not_normalized(self) -> None:
        for id_number in (' ' + TWN_VALID, TWN_VALID.lower()):
            with self.subTest(id_number=id_number):
                result = api.validate('tw', id_number)
                self.assertEqual(result.is_valid, TWN.NationalID.validate(id_number))
                self.assertEqual(result.id_number, id_number)

    def test_validator_that_raises(self) -> None:
        with isolated_registry():
            registry.register('QQQ', RaisingValidator, alpha2='QQ')
            result = api.validate('qq', 'x1')
        self.assertFalse(result.is_valid)
        self.assertEqual(result.country_code, 'QQQ')
        self.assertEqual(result.reason, api.FailureReason.VALIDATION_FAILED)
        self.assertEqual(result.error_message, 'RuntimeError: boom x1')
        self.assertIsNone(result.extracted_info)

    def test_parser_that_raises(self) -> None:
        with isolated_registry():
            registry.register('QQQ', RaisingParser, alpha2='QQ')
            result = api.validate('QQQ', 'x1')
        self.assertFalse(result.is_valid)
        self.assertEqual(result.country_code, 'QQQ')
        self.assertEqual(result.reason, api.FailureReason.VALIDATION_FAILED)
        self.assertEqual(result.error_message, 'ValueError: cannot parse')
        self.assertIsNone(result.extracted_info)

    def test_parser_that_returns_none(self) -> None:
        with isolated_registry():
            registry.register('QQQ', NoneParser, alpha2='QQ')
            result = api.validate('QQQ', 'x1')
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.extracted_info)
        self.assertIsNone(result.reason)

    def test_reason_is_set_iff_invalid(self) -> None:
        results = [
            api.validate('tw', TWN_VALID),
            api.validate('us', USA_VALID),
            api.validate('tw', TWN_INVALID),
            api.validate('XX', TWN_VALID),
        ]
        self.assertEqual([result.is_valid for result in results], [True, True, False, False])
        for result in results:
            with self.subTest(result=result):
                self.assertEqual(result.reason is None, result.is_valid)
                if result.is_valid:
                    self.assertIsNone(result.error_message)

    def test_matches_the_validator_on_the_parity_corpus(self) -> None:
        expanded = expand_corpus(load_corpus())
        self.assertEqual(len(expanded), 78)
        for alpha3, vectors in sorted(expanded.items()):
            with self.subTest(alpha3=alpha3):
                validator = registry.get_validator(alpha3)
                assert validator is not None
                for vector in vectors:
                    result = api.validate(alpha3, vector)
                    expected = validator.validate(vector)
                    if result.is_valid != expected or result.country_code != alpha3 or result.error_message:
                        self.fail('%s %r: %r, expected %r' % (alpha3, vector, result, expected))


class TestValidationResult(TestCase):
    def test_truthiness(self) -> None:
        self.assertTrue(api.validate('tw', TWN_VALID))
        self.assertFalse(api.validate('tw', TWN_INVALID))
        self.assertFalse(api.validate('XX', TWN_VALID))

    def test_is_frozen(self) -> None:
        result = api.validate('tw', TWN_VALID)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            result.is_valid = False  # type: ignore[misc]

    def test_defaults(self) -> None:
        result = api.ValidationResult(is_valid=False, country_code=None, id_number='x')
        self.assertIsNone(result.extracted_info)
        self.assertIsNone(result.reason)
        self.assertIsNone(result.error_message)


class TestFailureReason(TestCase):
    def test_values(self) -> None:
        self.assertEqual(
            {reason.name: reason.value for reason in api.FailureReason},
            {
                'UNSUPPORTED_COUNTRY': 'unsupported_country',
                'INVALID_LENGTH': 'invalid_length',
                'INVALID_FORMAT': 'invalid_format',
                'CHECKSUM_MISMATCH': 'checksum_mismatch',
                'INVALID_BIRTHDATE': 'invalid_birthdate',
                'VALIDATION_FAILED': 'validation_failed',
                'NOT_PARSABLE': 'not_parsable',
            },
        )

    def test_lookup_by_value_and_str(self) -> None:
        reason = api.FailureReason('checksum_mismatch')
        self.assertIs(reason, api.FailureReason.CHECKSUM_MISMATCH)
        self.assertIsInstance(reason, str)
        self.assertEqual(reason, 'checksum_mismatch')


class TestValidateMany(TestCase):
    def test_keeps_the_order(self) -> None:
        results = api.validate_many([('tw', TWN_VALID), ('XX', '1'), ('us', USA_VALID), ('tw', TWN_INVALID)])
        self.assertEqual([result.is_valid for result in results], [True, False, True, False])
        self.assertEqual([result.country_code for result in results], ['TWN', None, 'USA', 'TWN'])
        self.assertEqual(results[1].reason, api.FailureReason.UNSUPPORTED_COUNTRY)
        self.assertEqual(results[0], api.validate('tw', TWN_VALID))

    def test_accepts_any_iterable(self) -> None:
        pairs = iter([('tw', TWN_VALID), ('tw', TWN_INVALID)])
        self.assertEqual([bool(result) for result in api.validate_many(pairs)], [True, False])

    def test_empty(self) -> None:
        self.assertEqual(api.validate_many([]), [])


class TestPackageExports(TestCase):
    def test_reexports(self) -> None:
        self.assertIs(idnumbers.validate, api.validate)
        self.assertIs(idnumbers.validate_many, api.validate_many)
        self.assertIs(idnumbers.ValidationResult, api.ValidationResult)
        self.assertIs(idnumbers.FailureReason, api.FailureReason)

    def test_all(self) -> None:
        self.assertEqual(api.__all__, [
            'FailureReason', 'ValidationResult', 'ParseSuccess', 'ParseFailure', 'ParseIdInfoResult',
            'validate', 'validate_many', 'parse_id_info', 'failure_reason',
        ])
        for name in api.__all__:
            self.assertTrue(hasattr(api, name))


class TestLazyImport(TestCase):
    def run_code(self, code: str) -> None:
        env = dict(os.environ, PYTHONPATH=str(REPO_ROOT))
        subprocess.run([sys.executable, '-c', code], cwd=str(REPO_ROOT), env=env, check=True)

    def test_unsupported_country_loads_no_country_module(self) -> None:
        self.run_code(
            'import sys, idnumbers\n'
            "result = idnumbers.validate('XX', '1')\n"
            'assert not result.is_valid\n'
            "assert 'idnumbers.nationalid' not in sys.modules\n"
        )

    def test_validate_loads_only_that_country(self) -> None:
        self.run_code(
            'import sys, idnumbers\n'
            "assert idnumbers.validate('tw', 'A123456789').is_valid\n"
            "assert 'idnumbers.nationalid.TWN' in sys.modules\n"
            "assert 'idnumbers.nationalid.JPN' not in sys.modules\n"
        )


if __name__ == '__main__':
    main()
