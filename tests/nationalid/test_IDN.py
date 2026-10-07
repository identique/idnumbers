from unittest import TestCase, main

from idnumbers.nationalid import IDN
from idnumbers.nationalid.constant import Gender


class TestIDNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(IDN.NationalID.validate('7105100607610439'))
        self.assertTrue(IDN.NationalID.validate('7105102902040439'))

    def test_error_case(self):
        self.assertFalse(IDN.NationalID.validate('7105102902020439'))
        self.assertFalse(IDN.NationalID.validate('0950060607610439'))
        self.assertFalse(IDN.NationalID.validate('7105101613610439'))
        self.assertFalse(IDN.NationalID.validate('7105100607610000'))

    def test_parse(self):
        result = IDN.NationalID.parse('7105100607610439')
        self.assertEqual("06", result['dd'])
        self.assertEqual("07", result['mm'])
        self.assertEqual("61", result['yy'])
        self.assertEqual(Gender.MALE, result['gender'])

    def test_gender_and_day_encoding(self):
        # The other vectors are synthetic; the female vector is a python-stdnum
        # 2.2 doctest (1945-08-17).
        vectors = (
            ('3171011708450001', Gender.MALE, '17'),
            ('3171015708450001', Gender.FEMALE, '17'),
            ('3171017101900001', Gender.FEMALE, '31'),
        )
        for id_number, gender, day in vectors:
            with self.subTest(id_number=id_number):
                self.assertTrue(IDN.NationalID.validate(id_number))
                result = IDN.NationalID.parse(id_number)
                self.assertEqual(gender, result['gender'])
                self.assertEqual(day, result['dd'])

    def test_single_digit_day_padding_and_boundaries(self):
        vectors = (
            ('3171010101800001', Gender.MALE, '01'),
            ('3171013101800001', Gender.MALE, '31'),
            ('3171014101800001', Gender.FEMALE, '01'),
            ('3171017101800001', Gender.FEMALE, '31'),
        )
        for id_number, gender, day in vectors:
            with self.subTest(id_number=id_number):
                result = IDN.NationalID.parse(id_number)
                self.assertIsNotNone(result)
                self.assertTrue(IDN.NationalID.validate(id_number))
                self.assertEqual(gender, result['gender'])
                self.assertEqual(day, result['dd'])

    def test_invalid_encoded_days(self):
        invalid_days = (
            ('00',)
            + tuple(f'{day:02d}' for day in range(32, 41))
            + tuple(f'{day:02d}' for day in range(72, 80))
        )
        for encoded_day in invalid_days:
            id_number = f'317101{encoded_day}01800001'
            with self.subTest(encoded_day=encoded_day):
                self.assertFalse(IDN.NationalID.validate(id_number))
                self.assertIsNone(IDN.NationalID.parse(id_number))

    def test_century_ambiguous_leap_day(self):
        # NIK has only a two-digit year: 2000 is a leap year although 1900 is not.
        # The first two vectors are synthetic; the last is a python-stdnum 2.2 doctest.
        for id_number in ('3171012902000001', '3171016902000001',
                          '3171012902001234'):
            with self.subTest(id_number=id_number):
                self.assertTrue(IDN.NationalID.validate(id_number))
                self.assertEqual('29', IDN.NationalID.parse(id_number)['dd'])

    def test_impossible_birth_dates(self):
        for id_number in (
            '1101014002900001',  # day 40 is not an encoding
            '3171013104800001',  # 31 April
            '3171012902190001',  # 29 February in 1919 or 2019
            '3171016902190001',  # female encoding of 29 February
        ):
            with self.subTest(id_number=id_number):
                self.assertFalse(IDN.NationalID.validate(id_number))
                self.assertIsNone(IDN.NationalID.parse(id_number))

    def test_metadata_and_malformed_input(self):
        self.assertEqual('ID', IDN.NationalID.METADATA.iso3166_alpha2)
        self.assertIs(IDN.NIK, IDN.NationalID.METADATA.alias_of)

        for id_number in (
            None,
            3171011708450001,
            '',
            '3171011708450001\n',
            '٣١٧١٠١١٧٠٨٤٥٠٠٠١',
        ):
            with self.subTest(id_number=id_number):
                self.assertFalse(IDN.NationalID.validate(id_number))
                self.assertIsNone(IDN.NationalID.parse(id_number))


if __name__ == '__main__':
    main()
