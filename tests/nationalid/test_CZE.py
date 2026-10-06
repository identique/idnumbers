from datetime import date, timedelta
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


def _birth_number(birth_date: date, serial: str = '123', month_offset: int = 0) -> str:
    """Build a 10-digit birth number with a correct check digit (synthetic, for the tests)."""
    first_nine = '%02d%02d%02d%s' % (birth_date.year % 100, birth_date.month + month_offset, birth_date.day, serial)
    return first_nine + str(int(first_nine) % 11 % 10)


class TestCZEBirthNumberCentury(TestCase):
    """10 digit numbers exist from 1954 only, so yy 00-53 is 20yy and a future date is invalid."""

    def test_years_00_to_53_are_20yy(self):
        # synthetic numbers: 1 Jan 2003 (male), 1 Jan 2003 (female), 1 Jan 1954
        result = BirthNumber.parse('0301011238')
        self.assertEqual(date(2003, 1, 1), result['yyyymmdd'])
        self.assertEqual(Gender.MALE, result['gender'])
        woman = BirthNumber.parse(_birth_number(date(2003, 1, 1), month_offset=50))
        self.assertEqual(date(2003, 1, 1), woman['yyyymmdd'])
        self.assertEqual(Gender.FEMALE, woman['gender'])
        self.assertEqual(date(1954, 1, 1), BirthNumber.parse('5401011231')['yyyymmdd'])
        self.assertEqual(date(1999, 12, 31), BirthNumber.parse('9912311233')['yyyymmdd'])

    def test_extra_20_month_offset_is_kept(self):
        # since 2004 the month gets +20 when the serial numbers of a day run out (synthetic number)
        number = _birth_number(date(2005, 3, 4), month_offset=20)
        self.assertEqual('05230412', number[:8])
        self.assertEqual(date(2005, 3, 4), BirthNumber.parse(number)['yyyymmdd'])
        number = _birth_number(date(2005, 3, 4), month_offset=70)
        self.assertEqual(date(2005, 3, 4), BirthNumber.parse(number)['yyyymmdd'])
        self.assertEqual(Gender.FEMALE, BirthNumber.parse(number)['gender'])

    def test_years_50_to_53_are_not_read_as_1950s(self):
        # issue #288: 5001010003 is not 1 Jan 1950 (a 10 digit number cannot exist then), it would be 2050
        self.assertIsNone(BirthNumber.parse('5001010003'))
        self.assertFalse(BirthNumber.validate('5001010003'))
        self.assertFalse(BirthNumber.validate('5301010000'))

    def test_future_date_is_invalid(self):
        # relative to today so that the test does not depend on the clock (valid while the year is < 2054)
        today = date.today()
        self.assertTrue(BirthNumber.validate(_birth_number(today)))
        self.assertTrue(BirthNumber.validate(_birth_number(today - timedelta(days=1))))
        self.assertFalse(BirthNumber.validate(_birth_number(today + timedelta(days=1))))
        self.assertIsNone(BirthNumber.parse(_birth_number(today + timedelta(days=1))))


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
