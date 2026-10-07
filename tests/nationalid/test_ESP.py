from unittest import TestCase, main
from idnumbers.nationalid import ESP
from idnumbers.nationalid.util import validate_regexp


class TestESPNationalIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ESP.NationalID.validate('12345678Z'))
        self.assertTrue(ESP.NationalID.validate('10469226V'))

    def test_error_case(self):
        self.assertFalse(ESP.NationalID.validate('1234567A'))
        self.assertFalse(ESP.NationalID.validate('12345678A'))

    def assert_validation_and_checksum(self, candidate, expected):
        for cls in (ESP.DNI, ESP.NationalID):
            with self.subTest(id_type=cls.__name__, candidate=candidate):
                self.assertIs(expected, cls.validate(candidate))
                self.assertIs(expected, cls.checksum(candidate))

    def test_all_check_letters_accept_both_ascii_cases(self):
        # Synthetic payloads cover all residues of the official Ministry of Interior mod-23 table.
        for residue, letter in enumerate('TRWAGMYFPDXBNJZSQVHLCKE'):
            candidate = f'{residue:08d}{letter}'
            self.assert_validation_and_checksum(candidate, True)
            self.assert_validation_and_checksum(candidate.lower(), True)

    def test_surrounding_whitespace_is_stripped(self):
        # Python str.strip() includes NBSP and em space; this is input normalization, not an issuance rule.
        for whitespace in (' ', '\t', '\n', '\r', '\v', '\f', '\u00a0', '\u2003', ' \t\n\r\v\f'):
            for candidate in ('12345678Z', '12345678z'):
                for wrapped in (whitespace + candidate, candidate + whitespace, whitespace + candidate + whitespace):
                    self.assert_validation_and_checksum(wrapped, True)

    def test_wrong_check_letter_is_rejected_after_normalization(self):
        for residue, letter in enumerate('TRWAGMYFPDXBNJZSQVHLCKE'):
            wrong_letter = 'R' if letter == 'T' else 'T'
            self.assert_validation_and_checksum(f' \t{residue:08d}{wrong_letter.lower()}\n ', False)

    def test_leading_zero_and_all_zero_payloads_are_preserved(self):
        for candidate in ('00000000T', '00000001R', '00000015S'):
            self.assert_validation_and_checksum(candidate, True)
            self.assert_validation_and_checksum(' ' + candidate.lower() + ' ', True)

    def test_malformed_inputs_are_rejected_without_raising(self):
        candidates = (
            None, False, 0, 12345678, 12.5, [], {}, object(), b'12345678Z', bytearray(b'12345678Z'),
            '', ' ', '\t\n', '1234567Z', '123456789Z', '12345678', '12345678ZZ', '12345678-Z',
            'ES12345678Z', 'X1234567L', 'Y1234567X', 'Z1234567R', '1234 5678Z', '12345678 Z',
            '12345678\nZ', '12345678\tZ', '12345678\rZ', '12345678\vZ', '12345678\fZ',
            '12345678\u00a0Z', '12345678\u2003Z', '１２３４５６７８Z', '١٢٣٤٥٦٧٨Z', '1234567８Z',
            ' １２３４５６７８z ', '00000015ſ', '00000021K', ' 00000015ſ ', ' 00000021K ',
            '12345678Ｚ', '12345678é', '\u200b12345678Z', '12345678Z\u200b',
            '\ufeff12345678Z', '12345678Z\ufeff', '\x0012345678Z', '12345678Z\x00',
        )
        for candidate in candidates:
            self.assert_validation_and_checksum(candidate, False)

    def test_raw_metadata_accepts_ascii_cases_but_does_not_normalize(self):
        for cls in (ESP.DNI, ESP.NationalID):
            for candidate in ('12345678Z', '12345678z'):
                with self.subTest(id_type=cls.__name__, candidate=candidate):
                    self.assertIsNotNone(cls.METADATA.regexp.fullmatch(candidate))
                    self.assertTrue(validate_regexp(candidate, cls.METADATA.regexp))
            for candidate in (' 12345678z', '12345678z ', '12345678Z\n', '\n12345678Z',
                              '１２３４５６７８Z', '١٢٣٤٥٦٧٨Z', '00000015ſ', '00000021K'):
                with self.subTest(id_type=cls.__name__, candidate=candidate):
                    self.assertFalse(validate_regexp(candidate, cls.METADATA.regexp))


if __name__ == '__main__':
    main()
