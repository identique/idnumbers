from datetime import date
from unittest import TestCase, main

from idnumbers.nationalid.constant import Gender
from idnumbers.nationalid import ITA


class TestITAValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ITA.FiscalCode.validate('MRTMTT91D08F205J'))
        self.assertTrue(ITA.FiscalCode.validate('MLLSNT82P65Z404U'))

    def test_error_case(self):
        self.assertFalse(ITA.FiscalCode.validate('MRTMT91D08F205J'))
        self.assertFalse(ITA.FiscalCode.validate('MLLSNT82X65Z404U'))

    def test_parse(self):
        result = ITA.FiscalCode.parse('MLLSNT82P65Z404U')
        self.assertEqual('MLL', result['surname_consonants'])
        self.assertEqual('SNT', result['firstname_consonants'])
        self.assertEqual(1982, result['yyyymmdd'].year)
        self.assertEqual(9, result['yyyymmdd'].month)
        self.assertEqual(25, result['yyyymmdd'].day)
        self.assertEqual('Z404', result['area_code'])
        self.assertEqual('U', result['checksum'])

        result = ITA.FiscalCode.parse('MRTMTT91D08F205J')
        self.assertEqual('MRT', result['surname_consonants'])
        self.assertEqual('MTT', result['firstname_consonants'])
        self.assertEqual(1991, result['yyyymmdd'].year)
        self.assertEqual(4, result['yyyymmdd'].month)
        self.assertEqual(8, result['yyyymmdd'].day)
        self.assertEqual('F205', result['area_code'])
        self.assertEqual('J', result['checksum'])


class TestITAOmocodia(TestCase):
    """
    Omocodia: the seven numeric positions (year, day, area code digits) may be written as one of the letters
    L M N P Q R S T U V, which stand for 0 1 2 3 4 5 6 7 8 9.
    https://en.wikipedia.org/wiki/Italian_fiscal_code (Omocodia section)

    The vectors are the examples of issue #296 and codes built from the same base 'RSSMRA85M01H501'; the check
    letter is computed over the code as written. Each valid one was also accepted by python-stdnum 2.2
    (stdnum.it.codicefiscale.is_valid).
    """

    def test_letter_in_year_digits(self):
        self.assertTrue(ITA.FiscalCode.validate('RSSMRA8LM01H501W'))
        self.assertTrue(ITA.FiscalCode.validate('RSSMRALLM01H501H'))

    def test_letter_in_day_digits(self):
        self.assertTrue(ITA.FiscalCode.validate('RSSMRA85MLMH501T'))
        self.assertTrue(ITA.FiscalCode.validate('RSSMRA85M1MH501J'))
        self.assertTrue(ITA.FiscalCode.validate('RSSMRA85M4MH501M'))

    def test_letter_in_area_code_digits(self):
        self.assertTrue(ITA.FiscalCode.validate('RSSMRA85M01H50LU'))
        self.assertTrue(ITA.FiscalCode.validate('RSSMRA85M01H5LLF'))
        self.assertTrue(ITA.FiscalCode.validate('RSSMRA85M01HLLLW'))

    def test_letter_outside_lmnpqrstuv_is_invalid_without_raising(self):
        # 'A' is not an omocodia letter; the check letters are correct for the codes as written
        self.assertFalse(ITA.FiscalCode.validate('RSSMRAA5M01H501Y'))
        self.assertFalse(ITA.FiscalCode.validate('RSSMRA85M01H5A1Q'))
        self.assertFalse(ITA.FiscalCode.validate('RSSMRA85M01H5AAR'))
        self.assertIsNone(ITA.FiscalCode.parse('RSSMRAA5M01H501Y'))

    def test_omocodia_with_impossible_date_is_invalid(self):
        # day 00 written as 'LL', correct check letter
        self.assertFalse(ITA.FiscalCode.validate('RSSMRA85MLLH501F'))
        self.assertFalse(ITA.FiscalCode.validate('RSSMRALLMLLHLLLC'))

    def test_wrong_check_letter_of_omocodia_is_invalid(self):
        self.assertFalse(ITA.FiscalCode.validate('RSSMRA8LM01H501A'))
        self.assertFalse(ITA.FiscalCode.validate('RSSMRA85MLMH501W'))

    def test_parse_maps_the_letters_back(self):
        result = ITA.FiscalCode.parse('RSSMRA85M01H50LU')
        self.assertEqual('H500', result['area_code'])
        self.assertEqual(date(1985, 8, 1), result['yyyymmdd'])
        self.assertEqual('U', result['checksum'])

        result = ITA.FiscalCode.parse('RSSMRA8LM01H501W')
        self.assertEqual(date(1980, 8, 1), result['yyyymmdd'])
        self.assertEqual('H501', result['area_code'])

        result = ITA.FiscalCode.parse('RSSMRALLM01H501H')
        self.assertEqual(date(2000, 8, 1), result['yyyymmdd'])

        result = ITA.FiscalCode.parse('RSSMRA85M1MH501J')
        self.assertEqual(date(1985, 8, 11), result['yyyymmdd'])
        self.assertEqual(Gender.MALE, result['gender'])

        result = ITA.FiscalCode.parse('RSSMRA85M4MH501M')
        self.assertEqual(date(1985, 8, 1), result['yyyymmdd'])
        self.assertEqual(Gender.FEMALE, result['gender'])

        result = ITA.FiscalCode.parse('RSSMRA85M01HLLLW')
        self.assertEqual('H000', result['area_code'])

    def test_plain_code_matches_its_omocodia_variants(self):
        plain = ITA.FiscalCode.parse('RSSMRA85M01H501Q')
        self.assertTrue(ITA.FiscalCode.validate('RSSMRA85M01H501Q'))
        for variant in ('RSSMRA85MLMH501T', 'RSSMRA85M01H50LU', 'RSSMRA85M01HLLLW'):
            parsed = ITA.FiscalCode.parse(variant)
            self.assertEqual(plain['yyyymmdd'], parsed['yyyymmdd'])
            self.assertEqual(plain['gender'], parsed['gender'])


if __name__ == '__main__':
    main()
