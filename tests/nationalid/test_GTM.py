from unittest import TestCase

import idnumbers
from idnumbers import FailureReason
from idnumbers.nationalid import GTM
from idnumbers.nationalid.gtm.dpi import DPI

# All numbers are synthetic constructions from the approved CUI layout, not real people's IDs.


class TestGTM(TestCase):
    def test_metadata_and_exports(self):
        self.assertIs(GTM.DPI, DPI)
        self.assertIs(GTM.NationalID.METADATA.alias_of, DPI)
        self.assertEqual(DPI.METADATA.iso3166_alpha2, "GT")
        self.assertEqual(DPI.METADATA.country_name, "Guatemala")
        self.assertFalse(DPI.METADATA.checksum)
        self.assertIsNone(DPI.METADATA.checksum_algorithm)
        self.assertFalse(hasattr(DPI, "checksum"))
        self.assertFalse(hasattr(GTM.NationalID, "checksum"))
        self.assertTrue(DPI.validate(DPI.METADATA.example))

    def test_valid_structure(self):
        for value in ("1912345670101", "1912345672299", "0000000000101", "1912345660101", "1912345671806"):
            with self.subTest(value=value):
                self.assertTrue(DPI.validate(value))
                self.assertTrue(GTM.NationalID.validate(value))
        for digit in "0123456789":
            self.assertTrue(DPI.validate("19123456" + digit + "0101"))

    def test_invalid_structure(self):
        for value in (
            "1912345670001",
            "1912345672301",
            "1912345670100",
            "191234567010",
            "19123456701011",
            "191234567010A",
            "",
            "１９１２３４５６７０１０１",
            "١٩١٢٣٤٥٦٧٠١٠١",
            "191234567010１",
        ):
            with self.subTest(value=value):
                self.assertFalse(DPI.validate(value))
                self.assertIsNone(DPI.parse(value))

    def test_no_whitespace_or_separators(self):
        number = DPI.METADATA.example
        for separator in (" ", "\t", "\n", "\r", "\r\n", "\u00a0", "\u200b", "-", ".", "/", "(", ")"):
            for value in (separator + number, number + separator, number[:4] + separator + number[4:]):
                with self.subTest(value=value):
                    self.assertFalse(DPI.validate(value))
                    self.assertIsNone(DPI.parse(value))

    def test_non_string(self):
        for value in (None, 1912345670101, True, b"1912345670101", [], {}, 1.0):
            with self.subTest(value=value):
                self.assertFalse(DPI.validate(value))  # type: ignore[arg-type]
                self.assertIsNone(DPI.parse(value))  # type: ignore[arg-type]

    def test_parse_preserves_zeroes(self):
        expected = {"correlative": "00000000", "check_digit": "0", "department": "01", "municipality": "01"}
        self.assertEqual(DPI.parse("0000000000101"), expected)
        self.assertEqual(GTM.NationalID.parse("0000000000101"), expected)
        self.assertEqual(
            DPI.parse("1912345672299"),
            {"correlative": "19123456", "check_digit": "7", "department": "22", "municipality": "99"},
        )

    def test_unified_api_and_format(self):
        number = DPI.METADATA.example
        for country in ("GT", "gtm"):
            result = idnumbers.validate(country, number)
            self.assertTrue(result)
            self.assertEqual(result.country_code, "GTM")
            self.assertEqual(result.extracted_info, DPI.parse(number))
            info = idnumbers.parse_id_info(country, number)
            assert info.ok
            self.assertEqual(info.info, DPI.parse(number))
            self.assertEqual(idnumbers.format_id(country, number), number)
            self.assertEqual(idnumbers.normalize_id(country, number), number)
            mask = idnumbers.get_input_mask(country)
            assert mask is not None
            self.assertEqual(mask.masks, ("#############",))
            self.assertIsNotNone(mask.pattern.fullmatch(number))
        self.assertIsNone(idnumbers.failure_reason(DPI, "1912345660101"))
        for value, reason in (
            ("191234567010", FailureReason.INVALID_LENGTH),
            ("1912345670001", FailureReason.INVALID_FORMAT),
            ("1912345672301", FailureReason.INVALID_FORMAT),
            ("1912345670100", FailureReason.INVALID_FORMAT),
        ):
            self.assertEqual(idnumbers.failure_reason(DPI, value), reason)
            self.assertEqual(idnumbers.validate("GT", value).reason, reason)
            info = idnumbers.parse_id_info("GT", value)
            assert not info.ok
            self.assertEqual(info.reason, reason)
