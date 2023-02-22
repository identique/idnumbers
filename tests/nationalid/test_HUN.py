from unittest import TestCase, main

from idnumbers.nationalid import HUN


class TestHUNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(HUN.PersonalID.validate('3 110714 1231'))

    def test_error_case(self):
        self.assertFalse(HUN.PersonalID.validate('3 110714 1230'))

    def test_parse(self):
        result = HUN.PersonalID.parse('3 110714 1231')
        self.assertEqual(2011, result['yyyymmdd'].year)
        self.assertEqual(7, result['yyyymmdd'].month)
        self.assertEqual(14, result['yyyymmdd'].day)
        self.assertEqual('123', result['sn'])
        self.assertEqual(1, result['checksum'])
