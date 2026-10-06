from unittest import TestCase, main
from datetime import date

from idnumbers.nationalid import NOR
from idnumbers.nationalid.constant import Gender


class TestNORValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NOR.NationalID.validate('29029600013'))

    def test_error_case(self):
        self.assertFalse(NOR.NationalID.validate('29029600012'))

    def test_parse(self):
        result = NOR.NationalID.parse('29029600013')
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual(date(1996, 2, 29), result['yyyymmdd'])
        self.assertEqual('13', result['checksum'])


class TestNORImpossibleBirthDate(TestCase):
    """Issue #304: an impossible birth date made validate() and parse() raise ValueError instead of False and None.

    Every vector below has correct control digits (computed with the mod-11 weights of
    https://no.wikipedia.org/wiki/F%C3%B8dselsnummer), so only the birth date is wrong.
    """

    def test_impossible_dates_are_invalid(self):
        for number, why in [('31049912350', '31 April'),
                            ('30029912331', '30 February'),
                            ('00000000000', 'day 00 and month 00'),
                            ('01009912378', 'month 00')]:
            with self.subTest(number=number, why=why):
                self.assertTrue(NOR.NationalID.checksum(number))
                self.assertFalse(NOR.NationalID.validate(number))
                self.assertIsNone(NOR.NationalID.parse(number))

    def test_leap_day_of_a_non_leap_year_is_invalid(self):
        # 29 February 1997 does not exist; 29 February 1996 does (see test_parse)
        number = '29029700034'
        self.assertTrue(NOR.NationalID.checksum(number))
        self.assertFalse(NOR.NationalID.validate(number))
        self.assertIsNone(NOR.NationalID.parse(number))


if __name__ == '__main__':
    main()
