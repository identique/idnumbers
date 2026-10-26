from unittest import TestCase, main

from idnumbers import FailureReason, failure_reason
from idnumbers.nationalid import FIN
from idnumbers.nationalid.constant import Gender


class TestKORValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(FIN.PersonalIdentityCode.validate("131052-308T"))
        self.assertTrue(FIN.PersonalIdentityCode.validate("240147-632T"))

    def test_error_case(self):
        self.assertFalse(FIN.PersonalIdentityCode.validate("131052-308t"))
        self.assertFalse(FIN.PersonalIdentityCode.validate("131052-308A"))

    def test_individual_number_range(self):
        # DVV issues individual numbers 002-899; 000 and 001 are not issued and 900-999 are temporary codes.
        for value in ("131052-002X", "131052-003Y", "131052-898U", "131052-899V", "010100A002H", "010100A899E"):
            with self.subTest(value=value):
                self.assertTrue(FIN.PersonalIdentityCode.validate(value))
        for value in (
            "131052-000V",
            "131052-001W",
            "131052-900W",
            "131052-901X",
            "131052-9993",
            "280378-999U",
            "010100A000E",
            "010100A999N",
        ):
            with self.subTest(value=value):
                # The check character is correct; only the individual number is out of range.
                self.assertTrue(FIN.PersonalIdentityCode.checksum(value))
                self.assertFalse(FIN.PersonalIdentityCode.validate(value))
                self.assertIsNone(FIN.PersonalIdentityCode.parse(value))

    def test_failure_reasons_for_out_of_range_individual_numbers(self):
        # An impossible date is reported first, even when the individual number is also out of range.
        for value in ("310252-9998", "310252-0001"):
            with self.subTest(value=value):
                self.assertEqual(FailureReason.INVALID_BIRTHDATE, failure_reason(FIN.PersonalIdentityCode, value))
        # A real date with an out-of-range individual number is a plain validation failure.
        for value in ("131052-9993", "131052-001W"):
            with self.subTest(value=value):
                self.assertEqual(FailureReason.VALIDATION_FAILED, failure_reason(FIN.PersonalIdentityCode, value))

    def test_parse(self):
        result = FIN.PersonalIdentityCode.parse("131052-308T")
        self.assertEqual(1952, result["yyyymmdd"].year)
        self.assertEqual(10, result["yyyymmdd"].month)
        self.assertEqual(13, result["yyyymmdd"].day)
        self.assertEqual(Gender.FEMALE, result["gender"])
        self.assertEqual("308", result["sn"])
        self.assertEqual("T", result["checksum"])


if __name__ == "__main__":
    main()
