from unittest import TestCase, main

import idnumbers
from idnumbers.nationalid import CAN


class TestCANSINValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(CAN.SocialInsuranceNumber.validate("130692544"))
        self.assertTrue(CAN.SocialInsuranceNumber.validate("123456782"))
        self.assertTrue(CAN.NationalID.validate("123456782"))
        self.assertTrue(idnumbers.validate("CAN", "123456782").is_valid)

    def test_error_case(self):
        self.assertFalse(CAN.SocialInsuranceNumber.validate("130692545"))

    def test_unissued_prefixes_are_rejected(self):
        for number in ("046454286", "823456785", "000000000"):
            with self.subTest(number=number):
                self.assertTrue(CAN.SocialInsuranceNumber.checksum(number))
                self.assertFalse(CAN.SocialInsuranceNumber.validate(number))
                self.assertFalse(CAN.NationalID.validate(number))
                result = idnumbers.validate("CAN", number)
                self.assertFalse(result.is_valid)
                self.assertIs(result.reason, idnumbers.FailureReason.INVALID_FORMAT)

    def test_all_sin_prefixes(self):
        # Synthetic Luhn-valid numbers exercise every possible first digit.
        sin_numbers = (
            ("023456783", False),
            ("123456782", True),
            ("223456781", True),
            ("323456780", True),
            ("423456789", True),
            ("523456788", True),
            ("623456787", True),
            ("723456786", True),
            ("823456785", False),
            ("923456784", True),
        )

        for number, expected in sin_numbers:
            with self.subTest(prefix=number[0]):
                self.assertTrue(CAN.SocialInsuranceNumber.checksum(number))
                self.assertEqual(expected, CAN.SocialInsuranceNumber.validate(number))
                self.assertEqual(expected, CAN.NationalID.validate(number))
                result = idnumbers.validate("CAN", number)
                self.assertEqual(expected, result.is_valid)
                if not expected:
                    self.assertIs(result.reason, idnumbers.FailureReason.INVALID_FORMAT)

    def test_valid_prefix_with_bad_checksum_is_rejected(self):
        number = "123456783"

        self.assertFalse(CAN.SocialInsuranceNumber.checksum(number))
        self.assertFalse(CAN.SocialInsuranceNumber.validate(number))
        self.assertIs(
            idnumbers.validate("CAN", number).reason,
            idnumbers.FailureReason.CHECKSUM_MISMATCH,
        )

    def test_malformed_and_non_string_inputs_are_rejected(self):
        for number in (
            "12345678",
            "1234567820",
            "１２３４５６７８２",
            "123456782\n",
            "123 456 782",
            "123-456-782",
            "",
            123456782,
            None,
            b"123456782",
        ):
            with self.subTest(number=number):
                self.assertFalse(CAN.SocialInsuranceNumber.validate(number))

    def test_with_metadata(self):
        self.assertIsNotNone(CAN.SocialInsuranceNumber.METADATA)
        self.assertFalse(CAN.SocialInsuranceNumber.METADATA.parsable)
        self.assertTrue(CAN.SocialInsuranceNumber.METADATA.checksum)


if __name__ == "__main__":
    main()
