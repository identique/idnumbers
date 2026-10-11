"""Best-effort diagnostics: frozen witnesses and adversarial custom validators."""
import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from types import SimpleNamespace
from unittest import TestCase

import idnumbers
from idnumbers import FailureReason as R, api, failure_reason, parse_id_info, validate
from idnumbers.nationalid import AUS, BEL, ITA, LKA, TWN
from idnumbers.nationalid import util
from tests.helpers.failure_reasons import iter_reason_matrix
from tests.helpers.contract import CHECK_CHARACTER_INDEX, check_character_mutations
from tests.test_api import isolated_registry


def rejecting(pattern=r'(?P<checksum>\d)', checksum=None, validator=None):
    class Custom:
        METADATA = SimpleNamespace(regexp=re.compile(pattern), min_length=1, max_length=1)

        @staticmethod
        def validate(value):
            return False if validator is None else validator(value)
    if checksum is not None:
        Custom.checksum = staticmethod(checksum)
    return Custom


class TestReasonMatrix(TestCase):
    def test_all_classes(self):
        rows = list(iter_reason_matrix())
        self.assertEqual(len(rows), 105)
        for row in rows:
            self.assertTrue(row.checksum_note)
            self.assertTrue(row.birthdate_note)
            self.assertEqual(row.valid.id_number, row.id_class.METADATA.example)
            for vector in (row.valid, *row.length, row.format, row.checksum, row.birthdate):
                if vector is None:
                    continue
                with self.subTest(cls=row.key, value=vector.id_number, expected=vector.expected):
                    self.assertEqual(row.id_class.validate(vector.id_number), vector.expected is None)
                    self.assertEqual(failure_reason(row.id_class, vector.id_number), vector.expected)
                    # Primary aliases and both unified paths must agree with the per-class result.
                    primary = idnumbers.get_validator(row.country)
                    if primary.METADATA.alias_of is row.id_class:
                        self.assertEqual(failure_reason(primary, vector.id_number), vector.expected)
                        result = validate(row.country, vector.id_number)
                        parsed = parse_id_info(row.country, vector.id_number)
                        self.assertEqual(result.reason, vector.expected)
                        if vector.expected is not None:
                            self.assertEqual(parsed.reason, vector.expected)

    def test_checksum_witnesses_change_only_check_character(self):
        counts = {R.CHECKSUM_MISMATCH: 0, R.VALIDATION_FAILED: 0}
        for row in iter_reason_matrix():
            if row.checksum is None:
                continue
            with self.subTest(cls=row.key):
                self.assertIn(row.checksum.id_number, check_character_mutations(
                    row.valid.id_number, CHECK_CHARACTER_INDEX.get(row.key, -1)))
                self.assertIsNotNone(util.match_regexp(row.checksum.id_number, row.id_class.METADATA.regexp))
                self.assertFalse(row.id_class.validate(row.checksum.id_number))
                counts[row.checksum.expected] += 1
        self.assertEqual(counts, {R.CHECKSUM_MISMATCH: 60, R.VALIDATION_FAILED: 14})

    def test_all_date_migrations_have_witnesses(self):
        rows = list(iter_reason_matrix())
        expected_countries = {'ALB', 'BEL', 'BGR', 'BIH', 'CHN', 'CZE', 'DNK', 'EST', 'FIN', 'HUN', 'IDN',
                              'ISL', 'ITA', 'KAZ', 'KOR', 'KWT', 'LTU', 'LUX', 'LVA', 'MEX', 'MKD', 'MNE',
                              'MYS', 'NOR', 'POL', 'ROU', 'SRB', 'SVK', 'SVN', 'SWE', 'ZAF'}
        dated = [row for row in rows if row.birthdate is not None]
        self.assertEqual({row.country for row in dated}, expected_countries)
        self.assertEqual(len(dated), 34)
        self.assertTrue(all(row.birthdate.expected == R.INVALID_BIRTHDATE for row in dated))

    def test_legacy_date_policies(self):
        # Belgium's unknown month/day is valid and must not record a date error.
        for value in ('85000003306', '85010003313'):
            self.assertIsNone(failure_reason(BEL.NationalID, value))
        # ITA chooses 2000 first, falling back to 1900 only for future dates.
        self.assertEqual(ITA.FiscalCode.extract_birthday('00', 'B', '29')[0], date(2000, 2, 29))
        self.assertIsNone(ITA.FiscalCode.extract_birthday('99', 'B', '29'))
        # LKA's legacy day 366 rolls into the next year for non-leap years.
        self.assertEqual(util.birth_date(1990, 1, 1), date(1990, 1, 1))
        bad_year = '000001200001'
        # The old ordinal rules are deliberately not changed; year zero is a calendar failure.
        for digit in '0123456789':
            value = bad_year[:-1] + digit
            if LKA.NationalID.checksum(value):
                self.assertEqual(failure_reason(LKA.NationalID, value), R.INVALID_BIRTHDATE)
                break
        else:
            self.fail('No repaired LKA checksum')

    def test_ordinal_rollover_is_not_calendar_failure(self):
        base = '199036600001'
        witnesses = [base[:-1] + digit for digit in '0123456789' if LKA.NationalID.validate(base[:-1] + digit)]
        self.assertTrue(witnesses)
        for value in witnesses:
            self.assertEqual(LKA.NationalID.parse(value)['yyyymmdd'], date(1991, 1, 1))
            self.assertIsNone(failure_reason(LKA.NationalID, value))


class TestDerivation(TestCase):
    def test_exports(self):
        self.assertIs(idnumbers.failure_reason, api.failure_reason)
        self.assertIn('failure_reason', api.__all__)
        self.assertIsNone(failure_reason(AUS.MedicareNumber, '2123 45670 1'))

    def test_length_format_precedence(self):
        cls = rejecting(checksum=lambda value: False)
        for value, expected in [('', R.INVALID_LENGTH), ('11', R.INVALID_LENGTH), ('x', R.INVALID_FORMAT),
                                ('１', R.INVALID_FORMAT), ('1\n', R.CHECKSUM_MISMATCH)]:
            self.assertEqual(failure_reason(cls, value), expected)
        for value in (None, 1, b'1', [], object()):
            self.assertEqual(failure_reason(cls, value), R.INVALID_FORMAT)

    def test_separator_candidates_do_not_change_validity(self):
        self.assertEqual(failure_reason(TWN.NationalID, 'A12345'), R.INVALID_LENGTH)
        self.assertEqual(failure_reason(TWN.NationalID, 'A123456788'), R.CHECKSUM_MISMATCH)
        self.assertEqual(validate('ZA', '7602300675085').reason, R.INVALID_BIRTHDATE)
        cls = rejecting(checksum=lambda value: False)
        self.assertEqual(failure_reason(cls, ' (1) .-/\t'), R.CHECKSUM_MISMATCH)
        self.assertFalse(cls.validate(' (1) .-/\t'))
        # Original and stripped candidates both match: one inconclusive candidate prevents a checksum reason.
        cls = rejecting(r'\d[ .-]?', checksum=lambda value: False if len(value) == 2 else None)
        self.assertEqual(failure_reason(cls, '1 '), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(rejecting(r'\d ?', checksum=lambda value: False), '1 '), R.CHECKSUM_MISMATCH)
        self.assertEqual(failure_reason(TWN.NationalID, ' '+TWN.NationalID.METADATA.example), R.VALIDATION_FAILED)

    def test_checksum_return_contract(self):
        for computed, expected in [(False, R.CHECKSUM_MISMATCH), (True, R.VALIDATION_FAILED),
                                   (None, R.VALIDATION_FAILED), (0, R.CHECKSUM_MISMATCH),
                                   (1, R.VALIDATION_FAILED), ('X', R.CHECKSUM_MISMATCH)]:
            with self.subTest(computed=computed):
                self.assertEqual(failure_reason(rejecting(checksum=lambda value: computed), '1'), expected)
        self.assertEqual(failure_reason(rejecting(checksum=lambda value: 0), '0'), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(rejecting(r'\d', checksum=lambda value: 0), '1'), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(rejecting(r'(?P<checksum>2)?1', checksum=lambda value: 0), '1'),
                         R.VALIDATION_FAILED)

    def test_metadata_and_checksum_errors(self):
        def boom(value):
            raise RuntimeError('boom')
        for metadata in (None, SimpleNamespace(), SimpleNamespace(regexp='not compiled'),
                         SimpleNamespace(regexp=re.compile('x'), min_length=None, max_length=1)):
            cls = rejecting()
            cls.METADATA = metadata
            self.assertEqual(failure_reason(cls, '1'), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(rejecting(checksum=boom), '1'), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(rejecting(validator=boom), '1'), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(object, '1'), R.VALIDATION_FAILED)
        self.assertIsNone(failure_reason(rejecting(validator=lambda value: True), None))

    def test_birthdate_and_checksum_precedence(self):
        def bad_date(value):
            util.birth_date(2000, 2, 31)
            return False
        for computed, expected in [(False, R.CHECKSUM_MISMATCH), (None, R.INVALID_BIRTHDATE),
                                   (True, R.INVALID_BIRTHDATE)]:
            self.assertEqual(failure_reason(rejecting(checksum=lambda value: computed, validator=bad_date), '1'),
                             expected)
        self.assertEqual(failure_reason(rejecting(validator=bad_date), 'x'), R.INVALID_FORMAT)

    def test_trace_exception_cleanup(self):
        count = 0
        def later_boom(value):
            nonlocal count
            count += 1
            if count > 1:
                util.birth_date(2000, 2, 31)
                raise ValueError('traced exception')
            return False
        self.assertEqual(failure_reason(rejecting(validator=later_boom), '1'), R.VALIDATION_FAILED)
        self.assertIsNone(util._birth_date_trace.get())
        self.assertEqual(failure_reason(rejecting(), '1'), R.VALIDATION_FAILED)

    def test_unified_path_does_not_repeat_initial_validation(self):
        calls = []
        cls = rejecting(checksum=lambda value: False, validator=lambda value: calls.append(value) or False)
        self.assertEqual(api._check('QQQ', cls, '1').reason, R.CHECKSUM_MISMATCH)
        self.assertEqual(calls, ['1'])

    def test_custom_registry_lockstep(self):
        cls = rejecting(checksum=lambda value: False)
        cls.METADATA.iso3166_alpha2 = 'QQ'
        with isolated_registry():
            idnumbers.register('QQQ', cls, alpha2='QQ')
            self.assertEqual(validate('qq', '1').reason, R.CHECKSUM_MISMATCH)
            self.assertEqual(parse_id_info('QQQ', '1').reason, R.CHECKSUM_MISMATCH)


class TestTraceIsolation(TestCase):
    def test_helper_and_nested_contexts(self):
        self.assertIsNone(util._birth_date_trace.get())
        self.assertIsNone(util.birth_date(1900, 2, 29))
        self.assertIsNone(util._birth_date_trace.get())
        token = util._birth_date_trace.set(False)
        try:
            self.assertEqual(util.birth_date(2000, 2, 29), date(2000, 2, 29))
            self.assertFalse(util._birth_date_trace.get())
            inner = rejecting(validator=lambda value: util.birth_date(2000, 2, 31) is not None)
            self.assertEqual(failure_reason(inner, '1'), R.INVALID_BIRTHDATE)
            self.assertFalse(util._birth_date_trace.get())
            def outer(value):
                if util._birth_date_trace.get() is not None:
                    # Only the private derivation starts a new trace; nested calls restore it.
                    failure_reason(inner, '1')
                    self.assertFalse(util._birth_date_trace.get())
                return False
            self.assertEqual(failure_reason(rejecting(validator=outer), '1'), R.VALIDATION_FAILED)
            self.assertFalse(util._birth_date_trace.get())
            util.birth_date(2000, 2, 31)
            self.assertTrue(util._birth_date_trace.get())
        finally:
            util._birth_date_trace.reset(token)
        self.assertIsNone(util._birth_date_trace.get())

    def test_nested_unified_calls(self):
        inner = rejecting(validator=lambda value: util.birth_date(2000, 2, 31) is not None)
        inner.METADATA.iso3166_alpha2 = 'QQ'
        with isolated_registry():
            idnumbers.register('QQQ', inner, alpha2='QQ')
            for diagnose in (validate, parse_id_info):
                def outer(value):
                    traced = util._birth_date_trace.get()
                    self.assertEqual(diagnose('QQQ', '1').reason, R.INVALID_BIRTHDATE)
                    self.assertIs(util._birth_date_trace.get(), traced)
                    return False
                self.assertEqual(failure_reason(rejecting(validator=outer), '1'), R.VALIDATION_FAILED)
        self.assertIsNone(util._birth_date_trace.get())

    def test_threads(self):
        barrier = Barrier(2)
        def worker(invalid):
            token = util._birth_date_trace.set(False)
            try:
                if invalid:
                    util.birth_date(2000, 2, 31)
                barrier.wait(timeout=10)
                return util._birth_date_trace.get()
            finally:
                util._birth_date_trace.reset(token)
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(list(pool.map(worker, [True, False])), [True, False])
        self.assertIsNone(util._birth_date_trace.get())

    def test_async_tasks(self):
        async def worker(invalid):
            token = util._birth_date_trace.set(False)
            try:
                if invalid:
                    util.birth_date(2000, 2, 31)
                await asyncio.sleep(0)
                return util._birth_date_trace.get()
            finally:
                util._birth_date_trace.reset(token)
        async def run():
            return await asyncio.gather(worker(True), worker(False))
        self.assertEqual(asyncio.run(run()), [True, False])
        self.assertIsNone(util._birth_date_trace.get())
