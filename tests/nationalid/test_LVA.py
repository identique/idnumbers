import subprocess
import sys
from datetime import date
from unittest import TestCase, main

from idnumbers.nationalid import LVA


class TestLVAValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(LVA.get_validator('290156-11605').validate('290156-11605'))
        self.assertTrue(LVA.get_validator('323691-93794').validate('323691-93794'))

    def test_error_case(self):
        self.assertFalse(LVA.PersonalCode.validate('290156-11607'))

    def test_parse(self):
        result = LVA.OldPersonalCode.parse('290156-11605')
        self.assertEqual(1956, result['yyyymmdd'].year)
        self.assertEqual(1, result['yyyymmdd'].month)
        self.assertEqual(29, result['yyyymmdd'].day)
        self.assertEqual('160', result['sn'])
        self.assertEqual(5, result['checksum'])
        self.assertIsNone(LVA.OldPersonalCode.parse('323691-93794'))

    @staticmethod
    def make_code(body):
        # Synthetic vectors, not issued identities; independent of production helpers.
        weights = (1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
        digit = (1101 - sum(int(value) * weight for value, weight in zip(body, weights))) % 11 % 10
        return body + str(digit)

    @staticmethod
    def formats(code):
        return (code, code[:6] + '-' + code[6:])

    def test_checksum_correct_issue_regressions(self):
        for code in ('000000-00001', '310499-00002', '999999-00007'):
            for value in self.formats(code.replace('-', '')):
                with self.subTest(value=value):
                    self.assertEqual(int(value[-1]), LVA.PersonalCode.checksum(value))
                    self.assertFalse(LVA.PersonalCode.validate(value))
                    self.assertFalse(LVA.NationalID.validate(value))

    def test_valid_legacy_dates_and_parse_contract(self):
        cases = (
            ('0101000123', date(1800, 1, 1)),
            ('3112991123', date(1999, 12, 31)),
            ('0101002123', date(2000, 1, 1)),
            ('2902002123', date(2000, 2, 29)),
            ('2902040123', date(1804, 2, 29)),
            ('2902041123', date(1904, 2, 29)),
            ('2902042123', date(2004, 2, 29)),
        )
        for body, birthday in cases:
            for value in self.formats(self.make_code(body)):
                with self.subTest(value=value):
                    self.assertTrue(LVA.OldPersonalCode.validate(value))
                    self.assertTrue(LVA.PersonalCode.validate(value))
                    self.assertTrue(LVA.NationalID.validate(value))
                    self.assertEqual({
                        'yyyymmdd': birthday, 'sn': '123', 'checksum': int(value[-1])
                    }, LVA.OldPersonalCode.parse(value))

    def test_invalid_legacy_dates_and_centuries(self):
        bodies = ['2902000123', '2902001123', '2902012123', '2902051123',
                  '3104991123', '3002991123', '0001991123', '0100991123',
                  '0113991123']
        bodies.extend('010100' + str(century) + '123' for century in range(3, 10))
        for body in bodies:
            for value in self.formats(self.make_code(body)):
                with self.subTest(value=value):
                    self.assertEqual(int(value[-1]), LVA.PersonalCode.checksum(value))
                    self.assertFalse(LVA.PersonalCode.validate(value))
                    self.assertFalse(LVA.NationalID.validate(value))
                    self.assertFalse(LVA.OldPersonalCode.validate(value))
                    self.assertIsNone(LVA.OldPersonalCode.parse(value))

    def test_all_prefixes(self):
        for prefix in range(100):
            # Legacy prefixes are days in January 1900; modern codes need no date/century.
            body = '{:02d}01001123'.format(prefix)
            for value in self.formats(self.make_code(body)):
                with self.subTest(value=value):
                    self.assertEqual(int(value[-1]), LVA.PersonalCode.checksum(value))
                    self.assertEqual(1 <= prefix <= 39, LVA.PersonalCode.validate(value))
                    self.assertEqual(1 <= prefix <= 39, LVA.NationalID.validate(value))

    def test_modern_prefixes_do_not_encode_dates_or_centuries(self):
        for prefix in range(32, 40):
            for suffix in ('00000000', '13999999', '99999999'):
                code = self.make_code(str(prefix) + suffix)
                for value in self.formats(code):
                    with self.subTest(value=value):
                        self.assertTrue(LVA.PersonalCode.validate(value))
                        self.assertTrue(LVA.NationalID.validate(value))
                        self.assertIsNone(LVA.OldPersonalCode.parse(value))
                        wrong = value[:-1] + str((int(value[-1]) + 1) % 10)
                        self.assertFalse(LVA.PersonalCode.validate(wrong))
                        self.assertFalse(LVA.NationalID.validate(wrong))

    def test_wrong_legacy_checksum(self):
        for value in self.formats(self.make_code('0101001123')):
            wrong = value[:-1] + str((int(value[-1]) + 1) % 10)
            self.assertFalse(LVA.PersonalCode.validate(wrong))
            self.assertFalse(LVA.NationalID.validate(wrong))

    def test_malformed_input_contract(self):
        values = (None, 123, [], {}, b'29015611605', '', 'abc', '2901561160',
                  '290156116050', '290156--11605', '290156 11605',
                  '290156-11605\n', '２９０１５６１１６０５', '٢٩٠١٥٦١١٦٠٥')
        for value in values:
            with self.subTest(value=value):
                self.assertFalse(LVA.PersonalCode.validate(value))
                self.assertFalse(LVA.NationalID.validate(value))
                self.assertIsNone(LVA.PersonalCode.checksum(value))

    def test_primary_api_remains_nonparsable(self):
        self.assertFalse(LVA.PersonalCode.METADATA.parsable)
        self.assertFalse(hasattr(LVA.PersonalCode, 'parse'))
        self.assertFalse(hasattr(LVA.NationalID, 'parse'))

    def test_fresh_import_orders(self):
        modules = ('idnumbers.nationalid.lva.personal_code',
                   'idnumbers.nationalid.lva.old_personal_code')
        for order in (modules, modules[::-1]):
            with self.subTest(order=order):
                script = (
                    'import importlib; '
                    + '; '.join('importlib.import_module({!r})'.format(module) for module in order)
                    + '; from idnumbers.nationalid.lva.personal_code import PersonalCode; '
                    + 'assert PersonalCode.validate("290156-11605"); '
                    + 'assert not PersonalCode.validate("310499-00002")'
                )
                subprocess.run([sys.executable, '-c', script], check=True)

    def test_checksum_has_docstring(self):
        self.assertIsNotNone(LVA.PersonalCode.checksum.__doc__)


if __name__ == '__main__':
    main()
