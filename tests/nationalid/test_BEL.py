from unittest import TestCase, main

from idnumbers.nationalid import BEL
from idnumbers.nationalid.constant import Gender


class TestBELValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(BEL.NationalID.validate('93051822361'))
        self.assertTrue(BEL.NationalID.validate('93.05.18-223.61'))
        self.assertTrue(BEL.NationalID.validate('84122031560'))

    def test_error_case(self):
        self.assertFalse(BEL.NationalID.validate('930518 223 61'))

    def test_parse(self):
        result = BEL.NationalID.parse('93051822361')
        self.assertEqual(1993, result['yyyymmdd'].year)
        self.assertEqual(5, result['yyyymmdd'].month)
        self.assertEqual(18, result['yyyymmdd'].day)
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('223', result['sn'])
        self.assertEqual(61, result['checksum'])


if __name__ == '__main__':
    main()
