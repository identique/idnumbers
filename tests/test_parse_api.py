"""Contracts of the unified primary-ID parsing API."""

import dataclasses
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

import idnumbers
from idnumbers import api, registry
from idnumbers.nationalid import BEL, TWN
from tests import test_api
from tests.test_api import (
    NoneParser, RaisingParser, RaisingValidator,
    TWN_VALID, TWN_INVALID, USA_VALID, isolated_registry,
)


class SharedParser(NoneParser):
    info: Dict[str, Any] = {'value': 1}

    @staticmethod
    def parse(id_number: str) -> Dict[str, Any]:
        return SharedParser.info


class TestParseIdInfo(TestCase):
    def test_lookup_forms_and_info(self) -> None:
        for country in ('tw', 'TW', 'twn', 'TWN'):
            with self.subTest(country=country):
                result = api.parse_id_info(country, TWN_VALID)
                self.assertIsInstance(result, api.ParseSuccess)
                assert isinstance(result, api.ParseSuccess)
                self.assertIs(result.ok, True)
                self.assertEqual(result.country_code, 'TWN')
                self.assertEqual(result.id_number, TWN_VALID)
                self.assertEqual(result.info, TWN.NationalID.parse(TWN_VALID))

    def test_every_parsable_primary_example(self) -> None:
        count = 0
        for entry in registry.list_supported_countries():
            cls = entry.national_id
            if not cls.METADATA.parsable:
                continue
            count += 1
            with self.subTest(country=entry.alpha3):
                example = cls.METADATA.example
                expected = cls.parse(example)
                self.assertIsNotNone(expected)
                result = api.parse_id_info(entry.alpha3, example)
                self.assertIsInstance(result, api.ParseSuccess)
                assert isinstance(result, api.ParseSuccess)
                self.assertEqual(result.info, expected)
                self.assertEqual(result.country_code, entry.alpha3)
                self.assertEqual(result.id_number, example)
        self.assertEqual(count, 42)

    def test_registered_aliases_and_single_parser_call(self) -> None:
        with isolated_registry():
            registry.register('QQQ', SharedParser, alpha2='QQ', aliases=['custom'])
            for country in ('QQQ', 'qqq', 'QQ', 'qq', 'CUSTOM', 'custom'):
                with self.subTest(country=country), patch.object(SharedParser, 'parse', wraps=SharedParser.parse) as parser:
                    with patch.object(SharedParser, 'validate', wraps=SharedParser.validate) as validator:
                        result = api.parse_id_info(country, 'sample')
                    validator.assert_called_once_with('sample')
                    parser.assert_called_once_with('sample')
                    self.assertEqual(result, api.ParseSuccess('QQQ', 'sample', {'value': 1}))

    def test_invalid_inputs_match_validation_failures(self) -> None:
        for country, number in [('tw', TWN_INVALID), ('us', 'bad'), ('tw', ''), ('tw', ' ' + TWN_VALID),
                                ('tw', None), ('tw', 123), ('tw', b'A123456789')]:
            with self.subTest(country=country, number=number):
                expected = api.validate(country, number)  # type: ignore[arg-type]
                result = api.parse_id_info(country, number)  # type: ignore[arg-type]
                self.assertEqual(result, api.ParseFailure(expected.country_code, number, expected.reason,
                                                         expected.error_message))
                self.assertIs(result.ok, False)
                self.assertIs(result.id_number, number)

    def test_unsupported_country_takes_precedence(self) -> None:
        for country in ('XX', '', ' tw', 'ın', None, 1, b'TW', object()):
            with self.subTest(country=repr(country)):
                result = api.parse_id_info(country, '')  # type: ignore[arg-type]
                self.assertEqual(result, api.ParseFailure(None, '', api.FailureReason.UNSUPPORTED_COUNTRY,
                                                         'unsupported country: %r' % (country,)))

    def test_valid_nonparsable_primary(self) -> None:
        self.assertTrue(api.validate('us', USA_VALID).is_valid)
        self.assertEqual(api.parse_id_info('us', USA_VALID),
                         api.ParseFailure('USA', USA_VALID, api.FailureReason.NOT_PARSABLE))

    def test_valid_incomplete_bel_date(self) -> None:
        # Existing BEL regression vector: month 00 means an unknown month (#282).
        number = '85003003376'
        self.assertTrue(BEL.NationalID.validate(number))
        self.assertIsNone(BEL.NationalID.parse(number))
        self.assertEqual(api.parse_id_info('be', number),
                         api.ParseFailure('BEL', number, api.FailureReason.NOT_PARSABLE))

    def test_registered_none_parser(self) -> None:
        with isolated_registry():
            registry.register('QQQ', NoneParser, alpha2='QQ')
            self.assertEqual(api.parse_id_info('qq', 'sample'),
                             api.ParseFailure('QQQ', 'sample', api.FailureReason.NOT_PARSABLE))

    def test_exceptions_match_validation(self) -> None:
        for cls, message in ((RaisingValidator, 'RuntimeError: boom x1'), (RaisingParser, 'ValueError: cannot parse')):
            with self.subTest(validator=cls.__name__), isolated_registry():
                registry.register('QQQ', cls, alpha2='QQ')
                result = api.parse_id_info('qq', 'x1')
                self.assertEqual(result, api.ParseFailure('QQQ', 'x1', api.FailureReason.VALIDATION_FAILED, message))
                self.assertEqual(result.error_message, api.validate('qq', 'x1').error_message)

    def test_fields_frozen_and_info_fresh(self) -> None:
        failure = api.parse_id_info('XX', 'sample')
        with self.assertRaises(dataclasses.FrozenInstanceError):
            failure.id_number = 'changed'  # type: ignore[misc]
        with isolated_registry():
            registry.register('QQQ', SharedParser, alpha2='QQ')
            first = api.parse_id_info('qq', 'sample')
            second = api.parse_id_info('qq', 'sample')
        assert isinstance(first, api.ParseSuccess) and isinstance(second, api.ParseSuccess)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            first.country_code = 'changed'  # type: ignore[misc]
        assert isinstance(first.info, dict)
        self.assertIsNot(first.info, second.info)
        self.assertIsNot(first.info, SharedParser.info)
        first.info['value'] = 2
        self.assertEqual(second.info, {'value': 1})
        self.assertEqual(SharedParser.info, {'value': 1})

    def test_package_reexports(self) -> None:
        for name in ('parse_id_info', 'ParseSuccess', 'ParseFailure', 'ParseIdInfoResult'):
            self.assertIs(getattr(idnumbers, name), getattr(api, name))

    def test_lazy_imports(self) -> None:
        runner = test_api.TestLazyImport()
        runner.run_code(
            'import sys, idnumbers\n'
            "assert not idnumbers.parse_id_info('XX', '1').ok\n"
            "assert 'idnumbers.nationalid' not in sys.modules\n"
            "assert idnumbers.parse_id_info('tw', 'A123456789').ok\n"
            "assert 'idnumbers.nationalid.TWN' in sys.modules\n"
            "assert 'idnumbers.nationalid.JPN' not in sys.modules\n"
        )
