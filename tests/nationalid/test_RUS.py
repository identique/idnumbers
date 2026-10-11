from unittest import TestCase

import idnumbers
from idnumbers import FailureReason
from idnumbers.nationalid import RUS
from idnumbers.nationalid.rus.national_id import NationalID

# All vectors are synthetic layout witnesses, not claims about issued passports.


def layouts(compact):
    return (compact, compact[:4] + ' ' + compact[4:], compact[:2] + ' ' + compact[2:4] + ' ' + compact[4:])


class TestRUSValidation(TestCase):
    def test_valid_layouts_and_parse(self):
        for compact in ('1234567890', '0001000001', '9999999999', '0101000010'):
            for value in layouts(compact):
                with self.subTest(value=value):
                    self.assertTrue(NationalID.validate(value))
                    self.assertEqual(NationalID.parse(value), {'series': compact[:4], 'number': compact[4:]})

    def test_zero_fields_in_every_layout(self):
        for compact in ('0000567890', '1234000000', '0000000000'):
            for value in layouts(compact):
                with self.subTest(value=value):
                    self.assertFalse(NationalID.validate(value))
                    self.assertIsNone(NationalID.parse(value))
                    self.assertEqual(idnumbers.failure_reason(NationalID, value), FailureReason.VALIDATION_FAILED)

    def test_invalid_input(self):
        values = ('', '123456789', '12345678901', '1234-567890', '12 34567890', '123456 7890',
                  '12 3456 7890', '1234  567890', '12 34  567890', '12 345678 90',
                  '1234\t567890', '12\t34 567890', '1234\n567890', '1234\u00a0567890',
                  '1234\u200b567890', '１２３４５６７８９０', '١٢٣٤٥٦٧٨٩٠', '123456789０', '123456789A')
        values += tuple(boundary + value + ending for value in layouts('1234567890')
                        for boundary, ending in ((' ', ''), ('', ' '), ('\n', ''), ('', '\n'),
                                                 ('\t', ''), ('', '\t'), ('\u00a0', ''), ('', '\u200b')))
        for value in values:
            with self.subTest(value=value):
                self.assertFalse(NationalID.validate(value))
                self.assertIsNone(NationalID.parse(value))

    def test_non_string_input(self):
        for value in (None, 1234567890, b'1234567890', [], {}, True):
            with self.subTest(value=value):
                self.assertFalse(NationalID.validate(value))  # type: ignore[arg-type]
                self.assertIsNone(NationalID.parse(value))  # type: ignore[arg-type]

    def test_metadata_and_export(self):
        self.assertIs(RUS.NationalID, NationalID)
        self.assertEqual(NationalID.METADATA.iso3166_alpha2, 'RU')
        self.assertEqual(NationalID.METADATA.country_name, 'Russia')
        self.assertEqual(NationalID.METADATA.id_type, 'Internal Passport')
        self.assertEqual(NationalID.METADATA.min_length, 10)
        self.assertEqual(NationalID.METADATA.max_length, 10)
        self.assertTrue(NationalID.METADATA.parsable)
        self.assertFalse(NationalID.METADATA.checksum)
        self.assertIsNone(NationalID.METADATA.checksum_algorithm)
        self.assertFalse(hasattr(NationalID, 'checksum'))
        self.assertTrue(NationalID.validate(NationalID.METADATA.example))

    def test_unified_api_and_formatting(self):
        for country in ('RU', 'ru', 'RUS', 'rus'):
            self.assertIs(idnumbers.get_validator(country), NationalID)
            for value in layouts('0001000001'):
                result = idnumbers.validate(country, value)
                self.assertTrue(result)
                self.assertEqual(result.country_code, 'RUS')
                self.assertEqual(result.extracted_info, {'series': '0001', 'number': '000001'})
                parsed = idnumbers.parse_id_info(country, value)
                assert parsed.ok
                self.assertEqual(parsed.info, result.extracted_info)
                self.assertEqual(idnumbers.normalize_id(country, value), '0001000001')
                self.assertEqual(idnumbers.format_id(country, value), '0001 000001')
            mask = idnumbers.get_input_mask(country)
            assert mask is not None
            self.assertIsNotNone(mask.pattern.fullmatch('0001 000001'))
        for mask in NationalID.METADATA.masks:
            digits = iter('1234567890')
            rendered = ''.join(next(digits) if character == '#' else character for character in mask)
            self.assertEqual(mask.count('#'), 10)
            self.assertTrue(NationalID.validate(rendered))
            self.assertEqual(idnumbers.normalize_id('RU', rendered), '1234567890')
            self.assertEqual(idnumbers.format_id('RU', rendered), '1234 567890')

    def test_failure_reasons(self):
        self.assertIsNone(idnumbers.failure_reason(NationalID, '12 34 567890'))
        self.assertEqual(idnumbers.failure_reason(NationalID, '123456789'), FailureReason.INVALID_LENGTH)
        self.assertEqual(idnumbers.failure_reason(NationalID, '123456789A'), FailureReason.INVALID_FORMAT)
