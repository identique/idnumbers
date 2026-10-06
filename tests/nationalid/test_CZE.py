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
