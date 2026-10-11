from unittest import TestCase

import idnumbers
from idnumbers import FailureReason
from idnumbers.nationalid import SAU
from idnumbers.nationalid.constant import Citizenship
from idnumbers.nationalid.sau.national_id import NationalID

# All numbers are synthetic structural witnesses, not real people's IDs or claims about issued numbers.

LUHN_FAILING = ('1000000009', '2000000007', '1234567890')


class TestSAU(TestCase):
    def test_metadata_and_exports(self):
        self.assertIs(SAU.NationalID, NationalID)
        self.assertIsNone(NationalID.METADATA.alias_of)
        self.assertEqual(NationalID.METADATA.iso3166_alpha2, 'SA')
        self.assertEqual(NationalID.METADATA.country_name, 'Saudi Arabia')
        self.assertEqual(NationalID.METADATA.min_length, 10)
        self.assertEqual(NationalID.METADATA.max_length, 10)
        self.assertTrue(NationalID.METADATA.parsable)
        self.assertFalse(NationalID.METADATA.checksum)
        self.assertIsNone(NationalID.METADATA.checksum_algorithm)
        self.assertFalse(hasattr(NationalID, 'checksum'))
        self.assertFalse(hasattr(SAU.NationalID, 'checksum'))
        self.assertTrue(NationalID.validate(NationalID.METADATA.example))

    def test_valid_structure(self):
        for value in ('1000000008', '2000000006', '1999999999', '2000000000', '1234567890', '2234567891',
                      '1000000000', '2999999999'):
            with self.subTest(value=value):
                self.assertTrue(NationalID.validate(value))
                self.assertIsNotNone(NationalID.parse(value))

    def test_luhn_is_not_enforced(self):
        for value in LUHN_FAILING:
            with self.subTest(value=value):
                self.assertTrue(NationalID.validate(value))
        for digit in '0123456789':
            self.assertTrue(NationalID.validate('100000000' + digit))
            self.assertTrue(NationalID.validate('200000000' + digit))

    def test_invalid_structure(self):
        values = ['3000000008', '0000000000', '4000000008', '9000000008', '0123456789',
                  '', '1', '100000000', '10000000081', '20000000061', '100000000A', 'A000000008',
                  '1O00000008', '1000000008X', '1000000008.0',
                  '١٠٠٠٠٠٠٠٠٨', '１０００００００００', '100000000８', '٢٠٠٠٠٠٠٠٠٦']
        values += [str(first) + '000000008' for first in range(10) if first not in (1, 2)]
        for value in values:
            with self.subTest(value=value):
                self.assertFalse(NationalID.validate(value))
                self.assertIsNone(NationalID.parse(value))

    def test_no_whitespace_or_separators(self):
        for number in ('1000000008', '2000000006'):
            for separator in (' ', '\t', '\n', '\r', '\r\n', ' ', '​', '-', '.', '/', '(', ')'):
                for value in (separator + number, number + separator,
                              number[:5] + separator + number[5:], number[:1] + separator + number[1:]):
                    with self.subTest(value=value):
                        self.assertFalse(NationalID.validate(value))
                        self.assertIsNone(NationalID.parse(value))

    def test_non_string(self):
        for value in (None, 1000000008, True, b'1000000008', [], {}, 1.0):
            with self.subTest(value=value):
                self.assertFalse(NationalID.validate(value))  # type: ignore[arg-type]
                self.assertIsNone(NationalID.parse(value))  # type: ignore[arg-type]

    def test_parse_citizenship(self):
        for value in ('1000000008', '1999999999', '1000000009'):
            self.assertEqual(NationalID.parse(value), {'citizenship': Citizenship.CITIZEN})
            self.assertEqual(SAU.NationalID.parse(value), {'citizenship': Citizenship.CITIZEN})
        for value in ('2000000006', '2000000007', '2999999999'):
            self.assertEqual(NationalID.parse(value), {'citizenship': Citizenship.RESIDENT})
            self.assertEqual(SAU.NationalID.parse(value), {'citizenship': Citizenship.RESIDENT})

    def test_unified_api_and_format(self):
        number = NationalID.METADATA.example
        for country in ('SA', 'sa', 'SAU', 'sau'):
            self.assertIs(idnumbers.get_validator(country), NationalID)
            result = idnumbers.validate(country, number)
            self.assertTrue(result)
            self.assertEqual(result.country_code, 'SAU')
            self.assertEqual(result.extracted_info, {'citizenship': Citizenship.CITIZEN})
            info = idnumbers.parse_id_info(country, '2000000006')
            assert info.ok
            self.assertEqual(info.info, {'citizenship': Citizenship.RESIDENT})
            self.assertEqual(idnumbers.format_id(country, number), number)
            self.assertEqual(idnumbers.normalize_id(country, number), number)
            mask = idnumbers.get_input_mask(country)
            assert mask is not None
            self.assertEqual(mask.masks, ('##########',))
            self.assertIsNotNone(mask.pattern.fullmatch(number))
        self.assertIsNone(idnumbers.failure_reason(NationalID, '1000000009'))
        for value, reason in (('100000000', FailureReason.INVALID_LENGTH),
                              ('10000000081', FailureReason.INVALID_LENGTH),
                              ('3000000008', FailureReason.INVALID_FORMAT),
                              ('100000000A', FailureReason.INVALID_FORMAT),
                              ('1000000008\n', FailureReason.VALIDATION_FAILED)):
            self.assertEqual(idnumbers.failure_reason(NationalID, value), reason)
            self.assertEqual(idnumbers.validate('SA', value).reason, reason)
            info = idnumbers.parse_id_info('SA', value)
            assert not info.ok
            self.assertEqual(info.reason, reason)
