from unittest import TestCase, main

from idnumbers.nationalid import TWN
from idnumbers.nationalid.constant import Gender


class TestTWNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(TWN.NationalID.validate('A123456789'))
        self.assertTrue(TWN.NationalID.validate('M140051653'))
        self.assertTrue(TWN.NationalID.validate('Q238927307'))

    def test_error_case(self):
        self.assertFalse(TWN.NationalID.validate('A223456789'))
        self.assertFalse(TWN.NationalID.validate('m140051653'))

    def test_parse(self):
        result = TWN.NationalID.parse('A123456789')
        self.assertEqual('A', result['location'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('2345678', result['sn'])
        self.assertEqual(9, result['checksum'])


if __name__ == '__main__':
    main()
