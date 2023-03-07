from unittest import TestCase, main

from idnumbers.nationalid import SVK
from idnumbers.nationalid.constant import Gender


class TestSVKValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(SVK.BirthNumber.validate('605229/9011'))
        self.assertTrue(SVK.BirthNumber.validate('6052299011'))
        self.assertTrue(SVK.CitizenIDNumber.validate('XX024051'))
        self.assertTrue(SVK.CitizenIDNumber.validate('XX 024051'))

    def test_error_case(self):
        self.assertFalse(SVK.BirthNumber.validate('6052299010'))

    def test_parse(self):
        result = SVK.BirthNumber.parse('6052299011')
        self.assertEqual(1960, result['yyyymmdd'].year)
        self.assertEqual(2, result['yyyymmdd'].month)
        self.assertEqual(29, result['yyyymmdd'].day)
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('901', result['sn'])
        self.assertEqual(1, result['checksum'])


if __name__ == '__main__':
    main()
