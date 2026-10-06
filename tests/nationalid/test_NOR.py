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


class TestNORDAndHNumbers(TestCase):
    """Issue #304: D-numbers (day + 40) and H-numbers (month + 40), https://no.wikipedia.org/wiki/F%C3%B8dselsnummer

    The control digits are computed over the digits as written, and every vector below has correct ones.
    """

    def test_d_number(self):
        # from the issue: day 41 is 1 January 1999
        number = '41019912351'
        self.assertTrue(NOR.NationalID.validate(number))
        result = NOR.NationalID.parse(number)
        self.assertEqual(date(1999, 1, 1), result['yyyymmdd'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('51', result['checksum'])

    def test_d_number_range(self):
        # day 71 is the 31st
        self.assertTrue(NOR.NationalID.validate('71019912374'))
        self.assertEqual(date(1999, 1, 31), NOR.NationalID.parse('71019912374')['yyyymmdd'])

    def test_d_number_day_72_is_invalid(self):
        # day 72 would be 32, control digits are correct
        number = '72019912303'
        self.assertTrue(NOR.NationalID.checksum(number))
        self.assertFalse(NOR.NationalID.validate(number))
        self.assertIsNone(NOR.NationalID.parse(number))

    def test_d_number_with_impossible_date_is_invalid(self):
        # day 71 in April would be 31 April
        number = '71049912344'
        self.assertTrue(NOR.NationalID.checksum(number))
        self.assertFalse(NOR.NationalID.validate(number))
        self.assertIsNone(NOR.NationalID.parse(number))

    def test_h_number(self):
        # from the issue: month 41 is January, so 1 January 1999
        number = '01419912340'
        self.assertTrue(NOR.NationalID.validate(number))
        result = NOR.NationalID.parse(number)
        self.assertEqual(date(1999, 1, 1), result['yyyymmdd'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('40', result['checksum'])

    def test_h_number_range(self):
        number = '01529912389'  # month 52 is December
        self.assertTrue(NOR.NationalID.validate(number))
        self.assertEqual(date(1999, 12, 1), NOR.NationalID.parse(number)['yyyymmdd'])

    def test_h_number_month_53_is_invalid(self):
        # month 53 would be 13, control digits are correct
        number = '01539912379'
        self.assertTrue(NOR.NationalID.checksum(number))
        self.assertFalse(NOR.NationalID.validate(number))
        self.assertIsNone(NOR.NationalID.parse(number))

    def test_day_40_is_not_a_d_number(self):
        # day 40 is just below the D-number range 41-71; the control digits are computed with the no.wikipedia
        # mod-11 weights and python-stdnum 2.2 (stdnum.no.fodselsnummer) also rejects it
        number = '40019912312'
        self.assertTrue(NOR.NationalID.checksum(number))
        self.assertFalse(NOR.NationalID.validate(number))
        self.assertIsNone(NOR.NationalID.parse(number))

    def test_month_40_is_not_an_h_number(self):
        # month 40 is just below the H-number range 41-52; same source as the day 40 vector
        number = '01409912350'
        self.assertTrue(NOR.NationalID.checksum(number))
        self.assertFalse(NOR.NationalID.validate(number))
        self.assertIsNone(NOR.NationalID.parse(number))

    def test_d_and_h_numbers_use_the_century_table(self):
        # individual number 500-749 with yy >= 54 is 18xx; the control digits are computed with the no.wikipedia
        # mod-11 weights and python-stdnum 2.2 reads both as 1855-01-01
        for kind, number, checksum in [('D-number', '41015550072', '72'), ('H-number', '01415550061', '61')]:
            with self.subTest(kind=kind, number=number):
                self.assertTrue(NOR.NationalID.validate(number))
                result = NOR.NationalID.parse(number)
                self.assertEqual(date(1855, 1, 1), result['yyyymmdd'])
                self.assertEqual(Gender.FEMALE, result['gender'])
                self.assertEqual(checksum, result['checksum'])

    def test_wrong_checksum_is_still_invalid(self):
        self.assertFalse(NOR.NationalID.validate('41019912350'))
        self.assertFalse(NOR.NationalID.validate('01419912341'))

    def test_day_and_month_both_increased_is_invalid(self):
        # a D-number and an H-number at once is not a defined type (python-stdnum accepts it, the sources define the two separately)
        number = '41419912334'
        self.assertTrue(NOR.NationalID.checksum(number))
        self.assertFalse(NOR.NationalID.validate(number))
        self.assertIsNone(NOR.NationalID.parse(number))

    def test_fh_number_stays_invalid(self):
        # first digit 8 or 9: no birth date by design
        for number in ['80019912306', '90019912387']:
            with self.subTest(number=number):
                self.assertTrue(NOR.NationalID.checksum(number))
                self.assertFalse(NOR.NationalID.validate(number))
                self.assertIsNone(NOR.NationalID.parse(number))


if __name__ == '__main__':
    main()
