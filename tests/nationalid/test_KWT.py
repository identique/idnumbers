from unittest import TestCase

from idnumbers.nationalid import KWT


class TestKWTValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(KWT.CivilNumber.validate('291030104196'))
        self.assertTrue(KWT.CivilNumber.validate('279040907388'))
        self.assertTrue(KWT.CivilNumber.validate('288070804106'))

    def test_error_case(self):
        self.assertFalse(KWT.CivilNumber.validate('291030104197'))

    def test_parse(self):
        result = KWT.CivilNumber.parse('291030104196')
        self.assertEqual(1991, result['yyyymmdd'].year)
        self.assertEqual(3, result['yyyymmdd'].month)
        self.assertEqual(1, result['yyyymmdd'].day)
        self.assertEqual('0419', result['sn'])
        self.assertEqual(6, result['checksum'])

    def test_impossible_birth_date(self):
        # Source: issue #298. All three have a correct check digit, only the birth date is impossible.
        for value in (
            '200022900006',  # 29 Feb 1900, 1900 is not a leap year
            '200013200008',  # month 13
            '200001000009',  # month 00 and day 00
        ):
            with self.subTest(value=value):
                self.assertEqual(int(value[-1]), KWT.CivilNumber.checksum(value))
                self.assertFalse(KWT.CivilNumber.validate(value))
                self.assertIsNone(KWT.CivilNumber.parse(value))
