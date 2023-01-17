from unittest import TestCase, main
from datetime import date

from idnumbers.nationalid import BGR
from idnumbers.nationalid.constant import Gender


class TestBGRValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(BGR.UniformCivilNumber.validate('7501020018'))
        self.assertTrue(BGR.UniformCivilNumber.validate('7542011030'))

    def test_error_case(self):
        self.assertFalse(BGR.UniformCivilNumber.validate('7501020011'))
        self.assertFalse(BGR.UniformCivilNumber.validate('750102 0018'))

    def test_parse(self):
        result = BGR.UniformCivilNumber.parse('7501020018')
        self.assertEqual(date(1975, 1, 2), result['yyyymmdd'])
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual(8, result['checksum'])

        result = BGR.UniformCivilNumber.parse('7552010005')
        self.assertEqual(date(2075, 12, 1), result['yyyymmdd'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual(5, result['checksum'])


if __name__ == '__main__':
    main()
