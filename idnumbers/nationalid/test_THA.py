from unittest import TestCase, main

from idnumbers.nationalid import THA


class TestTHAValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(THA.NationalID.validate('3-8013-00141-07-4'))
        self.assertTrue(THA.NationalID.validate('3 8013 00141 07 4'))
        self.assertTrue(THA.NationalID.validate('3801300141074'))
        self.assertTrue(THA.NationalID.validate('3 6701 01122 56 9'))
        self.assertTrue(THA.NationalID.validate('3 4117 00830 33 4'))
        self.assertTrue(THA.NationalID.validate('1 9099 00064 64 0'))
        self.assertTrue(THA.NationalID.validate('5 9306 00015 56 7'))
        self.assertTrue(THA.NationalID.validate('2 9014 01009 21 1'))

    def test_error_case(self):
        self.assertFalse(THA.NationalID.validate('3-8013/00141-07-4'))
        self.assertFalse(THA.NationalID.validate('3 8010141 07 4'))
        self.assertFalse(THA.NationalID.validate('3801300141071'))

    def test_parse(self):
        result = THA.NationalID.parse('3 4117 00830 33 4')
        self.assertEqual(THA.ThaiCitizenship.CITIZEN_BEFORE_1984, result['citizenship'])
        self.assertEqual('41', result['province_code'])
        self.assertEqual('17', result['distinct_code'])
        self.assertEqual('0083033', result['sn'])
        self.assertEqual(4, result['checksum'])


if __name__ == '__main__':
    main()
