from unittest import TestCase, main

from idnumbers.nationalid import LUX


class TestLUXValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(LUX.NationalID.validate("1893120105732"))

    def test_error_case(self):
        self.assertFalse(LUX.NationalID.validate("1893120105733"))

    def test_parse(self):
        result = LUX.NationalID.parse("1893120105732")
        self.assertEqual(1893, result["yyyymmdd"].year)
        self.assertEqual(12, result["yyyymmdd"].month)
        self.assertEqual(1, result["yyyymmdd"].day)
        self.assertEqual("057", result["sn"])
        self.assertEqual(3, result["checksum1"])
        self.assertEqual(2, result["checksum2"])


class TestLUXEntityTINValidation(TestCase):
    # Synthetic vectors built from the OECD Luxembourg TIN sheet; no real entity numbers are published there.
    def test_normal_case(self):
        self.assertTrue(LUX.EntityTIN.validate("12345678903"))

    def test_remainder_zero_gives_check_digit_zero(self):
        self.assertTrue(LUX.EntityTIN.validate("19793000610"))

    def test_remainder_ten_gives_check_digit_one(self):
        self.assertTrue(LUX.EntityTIN.validate("19793000041"))

    def test_remainder_one_is_never_allocated(self):
        for check_digit in "0123456789":
            with self.subTest(check_digit=check_digit):
                self.assertFalse(LUX.EntityTIN.validate("1979300005" + check_digit))
                self.assertFalse(LUX.EntityTIN.checksum("1979300005" + check_digit))

    def test_error_case(self):
        self.assertFalse(LUX.EntityTIN.validate("12345678900"))
        self.assertFalse(LUX.EntityTIN.validate("1234567890"))
        self.assertFalse(LUX.EntityTIN.validate("123456789031"))
        self.assertFalse(LUX.EntityTIN.validate("1234567890A"))
        self.assertFalse(LUX.EntityTIN.validate("123 4567 8903"))
        self.assertFalse(LUX.EntityTIN.validate(""))
        self.assertFalse(LUX.EntityTIN.validate(None))
        self.assertFalse(LUX.EntityTIN.checksum(None))
        self.assertFalse(LUX.EntityTIN.checksum("1234567890"))

    def test_tin_namespace(self):
        self.assertIs(LUX.TIN.individual, LUX.NationalID)
        self.assertIs(LUX.TIN.entity, LUX.EntityTIN)
        self.assertTrue(LUX.TIN.individual.validate("1893120105732"))
        self.assertTrue(LUX.TIN.entity.validate("12345678903"))


if __name__ == "__main__":
    main()
