from unittest import TestCase, main

from idnumbers.nationalid import ISL


class TestISLValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ISL.NationalID.validate('010130-2989'))

    def test_error_case(self):
        self.assertFalse(ISL.NationalID.validate('010130-2979'))

    def test_parse(self):
        result = ISL.NationalID.parse('010130-2989')
        self.assertEqual(1930, result['yyyymmdd'].year)
        self.assertEqual(1, result['yyyymmdd'].month)
        self.assertEqual(1, result['yyyymmdd'].day)
        self.assertEqual('29', result['sn'])
        self.assertEqual(8, result['checksum'])
