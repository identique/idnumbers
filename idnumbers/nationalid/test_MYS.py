from unittest import TestCase, main

from idnumbers.nationalid import MYS
from idnumbers.nationalid.constant import Gender, Citizenship


class TestMYSValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(MYS.NationalID.validate('691206-10-5330'))
        self.assertTrue(MYS.NationalID.validate('510317-13-5131'))
        self.assertTrue(MYS.NationalID.validate('690602-13-6118'))
        self.assertTrue(MYS.NationalID.validate('801101-06-6085'))

    def test_error_case(self):
        self.assertFalse(MYS.NationalID.validate('6912010533'))

    def test_parse(self):
        result = MYS.NationalID.parse('690602-13-6118')
        self.assertEqual(1969, result['yyyymmdd'].year)
        self.assertEqual(6, result['yyyymmdd'].month)
        self.assertEqual(2, result['yyyymmdd'].day)
        self.assertEqual('13', result['location'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])
        self.assertEqual('6118', result['sn'])


if __name__ == '__main__':
    main()
