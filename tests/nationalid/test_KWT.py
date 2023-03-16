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
