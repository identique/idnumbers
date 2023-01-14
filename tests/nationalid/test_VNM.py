from unittest import TestCase, main

from idnumbers.nationalid import VNM
from idnumbers.nationalid.constant import Gender


class TestVNMValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(VNM.NationalID.validate('020093001656'))

    def test_error_case(self):
        self.assertFalse(VNM.NationalID.validate('0200930016561'))
        self.assertFalse(VNM.NationalID.validate('02009316561'))

    def test_parse(self):
        result = VNM.NationalID.parse('020093001656')
        self.assertEqual('020', result['province_country_code'])
        self.assertEqual(1993, result['yyyy'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('001656', result['sn'])


if __name__ == '__main__':
    main()
