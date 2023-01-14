from unittest import TestCase, main

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


if __name__ == '__main__':
    main()
