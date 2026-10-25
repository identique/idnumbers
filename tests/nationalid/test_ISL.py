from datetime import date
from unittest import TestCase

from idnumbers import FailureReason, failure_reason
from idnumbers.nationalid import ISL

# Þjóðskrá's synthetic kennitölur without a calculated check digit ("Kennitölur sem ekki standast vartölupróf"):
# https://www.skra.is/gogn/gervigogn-thjodskrar/
WITHOUT_CHECK_DIGIT = ("2811913049", "0209804299", "0404044400", "1005148220", "2412198560", "3003228340")


class TestISLValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ISL.NationalID.validate("010130-2989"))

    def test_registers_iceland_test_numbers_without_check_digit(self):
        for value in WITHOUT_CHECK_DIGIT:
            with self.subTest(value=value):
                self.assertTrue(ISL.NationalID.validate(value))
                self.assertTrue(ISL.NationalID.validate(value[:6] + "-" + value[6:]))
                self.assertIsNone(failure_reason(ISL.NationalID, value))

    def test_ninth_digit_is_not_checked(self):
        # Since 18 February 2026 the ninth digit is not a calculated check digit, so any digit is accepted.
        for digit in "0123456789":
            with self.subTest(digit=digit):
                self.assertTrue(ISL.NationalID.validate("010130-29" + digit + "9"))
        # Remainder 10 (check digit 1) under the pre-2026 rule, which kennitala-gem rejected.
        self.assertTrue(ISL.NationalID.validate("0101000119"))

    def test_no_checksum_method(self):
        self.assertFalse(ISL.NationalID.METADATA.checksum)
        self.assertIsNone(ISL.NationalID.METADATA.checksum_algorithm)
        self.assertFalse(hasattr(ISL.NationalID, "checksum"))

    def test_century_digit(self):
        # Þjóðskrá: the last digit is 8, 9 or 0 and gives the century of birth.
        self.assertEqual(date(1874, 1, 12), ISL.NationalID.parse("120174-3398")["yyyymmdd"])
        self.assertEqual(date(1974, 1, 12), ISL.NationalID.parse("120174-3399")["yyyymmdd"])
        self.assertEqual(date(2004, 4, 4), ISL.NationalID.parse("040404-4400")["yyyymmdd"])
        for digit in "1234567":
            with self.subTest(digit=digit):
                self.assertFalse(ISL.NationalID.validate("120174-339" + digit))
                self.assertIsNone(ISL.NationalID.parse("120174-339" + digit))

    def test_error_case(self):
        # 29 February: 1800 is not a leap year, 2000 is.
        self.assertFalse(ISL.NationalID.validate("290200-0008"))
        self.assertTrue(ISL.NationalID.validate("290200-0000"))
        self.assertFalse(ISL.NationalID.validate("310274-0899"))
        self.assertEqual(FailureReason.INVALID_BIRTHDATE, failure_reason(ISL.NationalID, "290200-0008"))
        self.assertFalse(ISL.NationalID.validate("010130-298"))
        self.assertFalse(ISL.NationalID.validate("01013-02989"))

    def test_parse(self):
        result = ISL.NationalID.parse("010130-2989")
        self.assertEqual(1930, result["yyyymmdd"].year)
        self.assertEqual(1, result["yyyymmdd"].month)
        self.assertEqual(1, result["yyyymmdd"].day)
        self.assertEqual("29", result["sn"])
        self.assertEqual(8, result["checksum"])

    def test_parse_returns_the_unverified_ninth_digit(self):
        result = ISL.NationalID.parse("281191-3049")
        self.assertEqual(date(1991, 11, 28), result["yyyymmdd"])
        self.assertEqual("30", result["sn"])
        self.assertEqual(4, result["checksum"])
