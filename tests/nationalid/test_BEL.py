from datetime import date
from unittest import TestCase

from idnumbers.nationalid import BEL
from idnumbers.nationalid.constant import Gender


class TestBELValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(BEL.NationalID.validate('93051822361'))
        self.assertTrue(BEL.NationalID.validate('93.05.18-223.61'))
        self.assertTrue(BEL.NationalID.validate('84122031560'))

    def test_error_case(self):
        self.assertFalse(BEL.NationalID.validate('930518 223 61'))

    def test_parse(self):
        result = BEL.NationalID.parse('93051822361')
        self.assertEqual(1993, result['yyyymmdd'].year)
        self.assertEqual(5, result['yyyymmdd'].month)
        self.assertEqual(18, result['yyyymmdd'].day)
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('223', result['sn'])
        self.assertEqual(61, result['checksum'])

    def test_tin_cases(self):
        self.assertTrue(BEL.TIN.individual.validate('93051822361'))
        self.assertTrue(BEL.TIN.entity.validate('0440966354'))
        self.assertTrue(BEL.TIN.entity.validate('0831797467'))
        self.assertTrue(BEL.TIN.entity.validate('831797467'))
        self.assertFalse(BEL.TIN.entity.validate('0440966353'))

    def test_century_is_inferred_from_the_check_digits(self):
        # Born from 2000: the check digits are computed with a leading 2
        # (IT000 "Het identificatienummer"; python-stdnum stdnum/be/nn.py).
        # 97 - (2000000000 + 010101001) % 97 = 26
        self.assertTrue(BEL.NationalID.validate('01010100126'))
        # npm#217 / parity allowlist entry, 2000-07-30
        self.assertTrue(BEL.NationalID.validate('00073003318'))
        # Born 1900-1949: yy < 50 does not mean 20yy. 97 - 470101001 % 97 = 90
        # (issue #282; stdnum.be.nn.is_valid is True)
        self.assertTrue(BEL.NationalID.validate('47010100190'))
        # IT000 example: a man born 1942-01-22
        self.assertTrue(BEL.NationalID.validate('42012205181'))

    def test_parse_uses_the_inferred_century(self):
        # 1 Jan 1950 has the 19xx check digits (stdnum get_birth_date is 1950-01-01), not 2050
        result = BEL.NationalID.parse('50010100156')
        self.assertEqual(date(1950, 1, 1), result['yyyymmdd'])
        self.assertEqual(date(2001, 1, 1), BEL.NationalID.parse('01010100126')['yyyymmdd'])
        self.assertEqual(date(1947, 1, 1), BEL.NationalID.parse('47010100190')['yyyymmdd'])
        self.assertEqual(date(1942, 1, 22), BEL.NationalID.parse('42012205181')['yyyymmdd'])

    def test_wrong_check_digits_are_rejected(self):
        # Synthetic: 29 = 97 - 2000000000 % 97, which the old precedence bug accepted for any yy < 50.
        # Under the real rules the check digits are 73 (19xx) or 05 (20xx), so 29 matches neither.
        self.assertFalse(BEL.NationalID.validate('00010100129'))
        self.assertIsNone(BEL.NationalID.parse('00010100129'))
        self.assertTrue(BEL.NationalID.checksum('00010100105'))
        self.assertTrue(BEL.NationalID.checksum('00010100173'))
        self.assertFalse(BEL.NationalID.checksum('00010100129'))

    def test_future_20xx_birth_year_is_rejected(self):
        # Synthetic: 2099-01-01 with the 2-prefixed check digits (97 - (2000000000 + 990101001) % 97 = 47)
        # is a birth in the future, so it is invalid.
        self.assertFalse(BEL.NationalID.validate('99010100147'))
        self.assertIsNone(BEL.NationalID.parse('99010100147'))
        # Synthetic control: the 19xx check digits (97 - 990101001 % 97 = 18) are a valid 1999 birth.
        self.assertTrue(BEL.NationalID.validate('99010100118'))
        self.assertEqual(1999, BEL.NationalID.parse('99010100118')['yyyymmdd'].year)

    def test_incomplete_birth_date_is_valid_but_not_parsable(self):
        # Month 00 = unknown month (issue #282; stdnum.be.nn.is_valid is True)
        self.assertTrue(BEL.NationalID.validate('85003003376'))
        self.assertIsNone(BEL.NationalID.parse('85003003376'))
        # IT000 examples: only the year is known (40 00 00 953 - 81), and the counter ran out (40 00 01 001 - 33)
        for id_number in ('40000095381', '40000100133'):
            self.assertTrue(BEL.NationalID.validate(id_number))
            self.assertIsNone(BEL.NationalID.parse(id_number))
        # Synthetic: a valid month with day 00, check digits 97 - 930500223 % 97 = 19
        self.assertTrue(BEL.NationalID.validate('93050022319'))
        self.assertIsNone(BEL.NationalID.parse('93050022319'))
        # A complete birth date still parses
        self.assertEqual(date(1993, 5, 18), BEL.NationalID.parse('93051822361')['yyyymmdd'])

    def test_impossible_birth_date_is_rejected(self):
        # Synthetic vectors with correct check digits, so only the date part is wrong
        self.assertFalse(BEL.NationalID.validate('93131822320'))  # month 13 (bis numbers are out of scope)
        self.assertFalse(BEL.NationalID.validate('93053222329'))  # day 32
        self.assertFalse(BEL.NationalID.validate('93023022368'))  # 30 February
        self.assertIsNone(BEL.NationalID.parse('93023022368'))

    def test_leap_day_depends_on_the_inferred_century(self):
        # Synthetic: 29 February 2000 exists (check digits use the leading 2: 45)
        self.assertTrue(BEL.NationalID.validate('00022900145'))
        self.assertEqual(date(2000, 2, 29), BEL.NationalID.parse('00022900145')['yyyymmdd'])
        # Synthetic: the same digits with the 19xx check digits (16) would be 29 February 1900, which does not exist
        self.assertFalse(BEL.NationalID.validate('00022900116'))

    def test_entity_vat_prefix(self):
        # Issue #282: the first digit of a 10-digit number is 0 or 1 (FOD Economie: the 1-series began
        # on 2023-09-19). The mod-97 check digits of 2000663602 are correct, but the prefix is not.
        self.assertFalse(BEL.TIN.entity.validate('2000663602'))
        self.assertFalse(BEL.TIN.entity.validate('9876543210'))
        # Synthetic 1-series number: 97 - 10000003 % 97 = 18
        self.assertTrue(BEL.TIN.entity.validate('1000000318'))
        self.assertFalse(BEL.TIN.entity.validate('1000000319'))
        # Synthetic: a 9-digit number has an implied leading 0, so its first digit may be 2 to 9.
        # 97 - 5123456 % 97 = 84, 97 - 9876543 % 97 = 94
        self.assertTrue(BEL.TIN.entity.validate('512345684'))
        self.assertTrue(BEL.TIN.entity.validate('987654394'))
        self.assertFalse(BEL.TIN.entity.validate('512345685'))
