from unittest import TestCase

from idnumbers.nationalid.CZE import TIN, BirthNumber
from idnumbers.nationalid.constant import Gender


class TestCZEBirthNumberCheckDigit(TestCase):
    """Birth number rules are shared with SVK, see also tests/nationalid/test_SVK.py."""

    def test_remainder_10_gives_check_digit_0(self):
        # The vectors come from issue #288 (checked with python-stdnum 2.2 cz.rc): the first nine digits
        # leave remainder 10 mod 11, so by law no. 133/2000 Sb. the check digit is 0.
        for number in ('5401031230', '5601011230', '540103/1230'):
            with self.subTest(number=number):
                self.assertTrue(BirthNumber.validate(number))
                self.assertTrue(BirthNumber.checksum(number))
        self.assertEqual(10, 540103123 % 11)
        self.assertNotEqual(0, 5401031230 % 11)

    def test_remainder_10_with_another_check_digit_is_invalid(self):
        for number in ('5401031231', '5401031239', '5601011231'):
            with self.subTest(number=number):
                self.assertFalse(BirthNumber.validate(number))

    def test_other_remainders_are_unchanged(self):
        # 7103192745 is the birth number example of python-stdnum cz.rc: the number is divisible by 11
        self.assertTrue(BirthNumber.validate('7103192745'))
        self.assertTrue(BirthNumber.validate('710319/2745'))
        self.assertFalse(BirthNumber.validate('7103192746'))
        self.assertFalse(BirthNumber.validate('7103192475'))

    def test_parse_remainder_10(self):
        result = BirthNumber.parse('5601011230')
        self.assertEqual(1956, result['yyyymmdd'].year)
        self.assertEqual(1, result['yyyymmdd'].month)
        self.assertEqual(1, result['yyyymmdd'].day)
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('123', result['sn'])
        self.assertEqual(0, result['checksum'])


class TestCZEBirthNumberNineDigits(TestCase):
    """Numbers given out up to 1953 have 9 digits and no check digit."""

    def test_nine_digits_before_1954_are_valid(self):
        # 530101123 comes from issue #288 (python-stdnum 2.2 cz.rc accepts it): 1 Jan 1953
        for number in ('530101123', '530101/123', '531231123', '535101123', '000101123'):
            with self.subTest(number=number):
                self.assertTrue(BirthNumber.validate(number))
                self.assertTrue(BirthNumber.checksum(number))

    def test_nine_digits_from_1954_are_invalid(self):
        # python-stdnum 2.2 cz.rc doctest: '590312/123' is a 9 digit number in 1959 and is rejected
        for number in ('540101123', '590312123', '590312/123', '700101123'):
            with self.subTest(number=number):
                self.assertFalse(BirthNumber.validate(number))

    def test_nine_digits_with_an_impossible_date_are_invalid(self):
        for number in ('530230123', '531301123', '530100123', '530132123', '530001123'):
            with self.subTest(number=number):
                self.assertFalse(BirthNumber.validate(number))

    def test_wrong_length_is_invalid(self):
        for number in ('53010112', '53010112300', '', '5301011234x'):
            with self.subTest(number=number):
                self.assertFalse(BirthNumber.validate(number))

    def test_parse_nine_digits_is_none(self):
        # there is no check digit to put in the result, as for a BEL number with an incomplete date
        self.assertIsNone(BirthNumber.parse('530101123'))
        self.assertIsNone(BirthNumber.parse('540101123'))

    def test_ten_digits_are_unchanged(self):
        self.assertIsNotNone(BirthNumber.parse('7103192745'))
        self.assertIsNone(BirthNumber.parse('7103192746'))


# the DIC of an individual is the birth number, except for 8 and 9 digit special cases
class TestCZETaxNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(TIN.individual.validate('7103192745'))
        self.assertTrue(TIN.individual.validate('6956220612'))
        self.assertTrue(TIN.individual.validate('654123789'))
        self.assertTrue(TIN.individual.validate('682127228'))
        self.assertTrue(TIN.individual.validate('48207926'))
        self.assertTrue(TIN.individual.validate('69663963'))
        self.assertTrue(TIN.individual.validate('25938002'))

    def test_error_case(self):
        self.assertFalse(TIN.individual.validate('71031'))
        self.assertFalse(TIN.individual.validate('682127229'))
        self.assertFalse(TIN.individual.validate('48207927'))
