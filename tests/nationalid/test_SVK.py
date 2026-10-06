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

    def test_remainder_10_gives_check_digit_0(self):
        # Issue #288, checked with python-stdnum 2.2 (sk.rc is cz.rc): the first nine digits leave
        # remainder 10 mod 11, so the check digit is 0 and the whole number is not divisible by 11.
        self.assertTrue(SVK.BirthNumber.validate('5401031230'))
        self.assertTrue(SVK.BirthNumber.validate('5601011230'))
        self.assertTrue(SVK.BirthNumber.validate('540103/1230'))
        self.assertTrue(SVK.BirthNumber.checksum('5401031230'))
        self.assertFalse(SVK.BirthNumber.validate('5401031231'))
        self.assertFalse(SVK.BirthNumber.validate('5601011239'))

    def test_nine_digits_before_1954(self):
        # Issue #288, python-stdnum 2.2 (sk.rc is cz.rc): 9-digit numbers have no check digit, up to 1953
        self.assertTrue(SVK.BirthNumber.validate('530101123'))
        self.assertTrue(SVK.BirthNumber.validate('530101/123'))
        self.assertFalse(SVK.BirthNumber.validate('540101123'))
        self.assertFalse(SVK.BirthNumber.validate('530230123'))
        self.assertIsNone(SVK.BirthNumber.parse('530101123'))

    def test_century_of_ten_digit_numbers(self):
        # 10-digit numbers exist from 1954, so yy 00-53 is 20yy (synthetic: 1 Jan 2003 and 1 Jan 1954)
        self.assertEqual(2003, SVK.BirthNumber.parse('0301011238')['yyyymmdd'].year)
        self.assertEqual(1954, SVK.BirthNumber.parse('5401011231')['yyyymmdd'].year)
        # issue #288: 2050 is in the future, it is not 1950
        self.assertFalse(SVK.BirthNumber.validate('5001010003'))
        self.assertIsNone(SVK.BirthNumber.parse('5001010003'))

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
