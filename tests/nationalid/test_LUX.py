from unittest import TestCase, main

from idnumbers.nationalid import LUX


class TestLUXValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(LUX.NationalID.validate('1893120105732'))

    def test_error_case(self):
        self.assertFalse(LUX.NationalID.validate('1893120105733'))

    def test_parse(self):
        result = LUX.NationalID.parse('1893120105732')
        self.assertEqual(1893, result['yyyymmdd'].year)
        self.assertEqual(12, result['yyyymmdd'].month)
        self.assertEqual(1, result['yyyymmdd'].day)
        self.assertEqual('057', result['sn'])
        self.assertEqual(3, result['checksum1'])
        self.assertEqual(2, result['checksum2'])


if __name__ == '__main__':
    main()
