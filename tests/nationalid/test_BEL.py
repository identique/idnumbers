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
