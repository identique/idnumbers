from unittest import TestCase
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

    def test_remainder_10_gives_check_digit_0(self):
        # 8507300050 and 0001011000: from the issue #283 report. Both have a weighted sum of 10 mod 11, so the
        # check digit is 0 (https://en.wikipedia.org/wiki/Unique_citizenship_number,
        # python-stdnum stdnum/bg/egn.py calc_check_digit: sum % 11 % 10).
        for number in ('8507300050', '0001011000'):
            self.assertTrue(BGR.UniformCivilNumber.validate(number), number)
            self.assertEqual(0, BGR.UniformCivilNumber.checksum(number), number)
        result = BGR.UniformCivilNumber.parse('8507300050')
        self.assertEqual(date(1985, 7, 30), result['yyyymmdd'])
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual(0, result['checksum'])
        result = BGR.UniformCivilNumber.parse('0001011000')
        self.assertEqual(date(1900, 1, 1), result['yyyymmdd'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual(0, result['checksum'])
        # synthetic: 990615006 has a weighted sum of 10 mod 11, so only check digit 0 is valid
        self.assertTrue(BGR.UniformCivilNumber.validate('9906150060'))
        self.assertEqual(date(1999, 6, 15), BGR.UniformCivilNumber.parse('9906150060')['yyyymmdd'])
        for check_digit in range(1, 10):
            self.assertFalse(BGR.UniformCivilNumber.validate('990615006%d' % check_digit), check_digit)
            self.assertFalse(BGR.UniformCivilNumber.validate('850730005%d' % check_digit), check_digit)

    def test_checksum_range(self):
        # the check digit is always a single digit; remainder 10 is mapped to 0
        self.assertEqual(8, BGR.UniformCivilNumber.checksum('7501020018'))
        self.assertEqual(5, BGR.UniformCivilNumber.checksum('7552010005'))
        self.assertEqual(0, BGR.UniformCivilNumber.checksum('9906150060'))

    def test_tin_cases(self):
        self.assertTrue(BGR.TIN.individual.validate('7501020018'))
        # test cases: https://papagal.bg/bg/
        self.assertTrue(BGR.TIN.entity.validate('207258749'))
        self.assertTrue(BGR.TIN.entity.validate('207271885'))
        self.assertTrue(BGR.TIN.entity.validate('114635815'))
