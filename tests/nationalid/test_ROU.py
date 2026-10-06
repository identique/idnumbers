from datetime import date
from unittest import TestCase, main

from idnumbers.nationalid import ROU
from idnumbers.nationalid.constant import Citizenship, Gender


class TestROUValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ROU.PersonalNumericalCode.validate('1800101221144'))
        self.assertTrue(ROU.PersonalNumericalCode.validate('1891113341181'))
        self.assertTrue(ROU.PersonalNumericalCode.validate('1831211379814'))
        self.assertTrue(ROU.PersonalNumericalCode.validate('2891202133223'))

    def test_error_case(self):
        self.assertFalse(ROU.PersonalNumericalCode.validate('1800101221143'))

    def test_parse(self):
        result = ROU.PersonalNumericalCode.parse('1800101221144')
        self.assertEqual(1980, result['yyyymmdd'].year)
        self.assertEqual(1, result['yyyymmdd'].month)
        self.assertEqual(1, result['yyyymmdd'].day)
        self.assertEqual('22', result['location'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])
        self.assertEqual('114', result['sn'])
        self.assertEqual(4, result['checksum'])


class TestROUCentury(TestCase):
    """
    Vectors come from issue #308 (differential comparison with the Node port) and were cross-checked with
    python-stdnum 2.2 ro.cnp. Check digits are computed with the CNP weights 279146358279.
    """

    def test_first_digit_6_does_not_raise(self):
        self.assertTrue(ROU.PersonalNumericalCode.validate('6050315121230'))
        result = ROU.PersonalNumericalCode.parse('6050315121230')
        self.assertEqual(date(2005, 3, 15), result['yyyymmdd'])
        self.assertEqual(Gender.FEMALE, result['gender'])

    def test_century_by_first_digit(self):
        cases = [
            ('6050315121230', date(2005, 3, 15), Gender.FEMALE),
            ('5050315121239', date(2005, 3, 15), Gender.MALE),
            ('2990101121231', date(1999, 1, 1), Gender.FEMALE),
            ('4990101121233', date(1899, 1, 1), Gender.FEMALE),
            ('3990101121231', date(1899, 1, 1), Gender.MALE),
            ('1800101221144', date(1980, 1, 1), Gender.MALE),
        ]
        for value, expected_date, expected_gender in cases:
            with self.subTest(value=value):
                self.assertTrue(ROU.PersonalNumericalCode.validate(value))
                result = ROU.PersonalNumericalCode.parse(value)
                self.assertEqual(expected_date, result['yyyymmdd'])
                self.assertEqual(expected_gender, result['gender'])

    def test_nonexistent_leap_day_1800(self):
        # 1800 is not a leap year, so 29 Feb 1800 does not exist
        self.assertFalse(ROU.PersonalNumericalCode.validate('4000229011237'))
        self.assertIsNone(ROU.PersonalNumericalCode.parse('4000229011237'))


if __name__ == '__main__':
    main()
