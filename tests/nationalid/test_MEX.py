from unittest import TestCase, main

from idnumbers.nationalid import MEX
from idnumbers.nationalid.constant import Gender


class TestMEXValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(MEX.NationalID.validate('HEGG560427MVZRRL04'))
        self.assertTrue(MEX.NationalID.validate('AUAM630703HGTGRR02'))
        self.assertTrue(MEX.NationalID.validate('HORA500201MNELSR04'))
        self.assertTrue(MEX.NationalID.validate('CAMP800404HNEHDD03'))
        self.assertTrue(MEX.NationalID.validate('DIXM870113HNEFXS06'))
        self.assertTrue(MEX.NationalID.validate('MACD880521HNERVN09'))
        self.assertTrue(MEX.NationalID.validate('DIXB881003HNELXB01'))
        self.assertTrue(MEX.NationalID.validate('SOMD911221HNEBJN03'))

    def test_error_case(self):
        self.assertFalse(MEX.NationalID.validate('HEGG560427MVZRRL05'))
        self.assertFalse(MEX.NationalID.validate('AUAM630703KGTGRR02'))
        self.assertFalse(MEX.NationalID.validate('HEGGGG0427MVZRRL05'))
        self.assertFalse(MEX.NationalID.validate('HEGG560427MXXRRL05'))

    def test_parse(self):
        result = MEX.NationalID.parse('HEGG560427MVZRRL04')
        self.assertEqual('HEGG', result['name_initial_chars'])
        self.assertEqual(1956, result['yyyymmdd'].year)
        self.assertEqual(4, result['yyyymmdd'].month)
        self.assertEqual(27, result['yyyymmdd'].day)
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('VZ', result['location'])
        self.assertEqual('RRL', result['name_consonants'])
        self.assertEqual('0', result['sn'])
        self.assertEqual(4, result['checksum'])


if __name__ == '__main__':
    main()
