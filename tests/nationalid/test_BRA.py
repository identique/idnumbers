from unittest import TestCase, main

from idnumbers.nationalid import BRA
from idnumbers.nationalid.util import match_regexp


class TestBRARGNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(BRA.RGNumber.validate("39.985.676-6"))
        self.assertTrue(BRA.RGNumber.validate("56.843.539-4"))
        self.assertTrue(BRA.RGNumber.validate("00.000.005-X"))

    def test_error_case(self):
        self.assertFalse(BRA.RGNumber.validate("39.985.676-5"))
        self.assertFalse(BRA.RGNumber.validate("56.843.539-X"))

    def test_regexp_rejects_pipe_as_check_character(self):
        # the check character class must not contain a literal '|' (#370); it is the regexp that has to
        # reject it, not just the checksum guard
        self.assertIsNone(match_regexp("12.345.678-|", BRA.RGNumber.METADATA.regexp))
        self.assertFalse(BRA.RGNumber.validate("12.345.678-|"))
        self.assertIsNotNone(match_regexp("00.000.005-X", BRA.RGNumber.METADATA.regexp))
        self.assertTrue(BRA.RGNumber.validate("00.000.005-X"))
        self.assertTrue(BRA.RGNumber.validate("39.985.676-6"))

    def test_modulus_zero_and_one_check_characters(self):
        # Synthetic prefixes: weighted sums are 0, 45 and 264, respectively.
        for number, expected in (
            ("00.000.000-X", False),
            ("00.000.000-0", True),
            ("00.000.005-X", True),
            ("00.000.005-0", False),
            ("99.953.539-X", False),
            ("99.953.539-0", True),
        ):
            with self.subTest(number=number):
                self.assertEqual(BRA.RGNumber.checksum(number), expected)
                self.assertEqual(BRA.RGNumber.validate(number), expected)

    def test_every_remainder_accepts_only_its_check_character(self):
        # Independent arithmetic over synthetic nonzero prefixes, not the production helper or multipliers.
        remainders = set()
        for prefix in range(10000000, 10000100):
            digits = str(prefix)
            weighted_sum = sum(int(digit) * weight for digit, weight in zip(digits, range(2, 10)))
            remainder = weighted_sum % 11
            if remainder in remainders:
                continue
            remainders.add(remainder)
            complement = (-weighted_sum) % 11
            expected_character = "X" if complement == 10 else str(complement)
            for character in "0123456789X":
                number = f"{digits[:2]}.{digits[2:5]}.{digits[5:]}-{character}"
                with self.subTest(remainder=remainder, number=number):
                    expected = character == expected_character
                    self.assertEqual(BRA.RGNumber.checksum(number), expected)
                    self.assertEqual(BRA.RGNumber.validate(number), expected)
        self.assertEqual(remainders, set(range(11)))

    def test_malformed_inputs_are_rejected(self):
        for number in (None, 0, b"00.000.005-X", "", "00000005X", "00.000.005-x", "00.000.005-X\n"):
            with self.subTest(number=number):
                self.assertFalse(BRA.RGNumber.checksum(number))
                self.assertFalse(BRA.RGNumber.validate(number))

    def test_with_metadata(self):
        self.assertIsNotNone(BRA.RGNumber.METADATA)
        self.assertTrue(BRA.RGNumber.METADATA.checksum)


class TestBRACPFNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(BRA.CPFNumber.validate("111.333.666-86"))

    def test_error_case(self):
        self.assertFalse(BRA.CPFNumber.validate("111.333.666-81"))

    def test_with_metadata(self):
        self.assertIsNotNone(BRA.CPFNumber.METADATA)
        self.assertTrue(BRA.CPFNumber.METADATA.checksum)

    def test_repeated_digit_numbers_are_rejected(self):
        for digit in "0123456789":
            for number in (digit * 11, f"{digit * 3}.{digit * 3}.{digit * 3}-{digit * 2}"):
                with self.subTest(number=number):
                    self.assertFalse(BRA.CPFNumber.validate(number))
                    self.assertFalse(BRA.NationalID.validate(number))

    def test_repeated_digit_rule_is_separate_from_checksum(self):
        # The repeated digits pass the check digits, so checksum() stays the pure check-digit computation
        self.assertTrue(BRA.CPFNumber.checksum("111.111.111-11"))
        self.assertFalse(BRA.CPFNumber.validate("111.111.111-11"))
        self.assertTrue(BRA.CPFNumber.validate("111.333.666-86"))


if __name__ == "__main__":
    main()
