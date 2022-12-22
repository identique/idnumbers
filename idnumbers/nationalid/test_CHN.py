from unittest import TestCase, main

from idnumbers.nationalid import CHN
from idnumbers.nationalid.constant import Gender


class TestCHNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(CHN.ResidentIDNumber.validate('11010219840406970X'))
        self.assertTrue(CHN.ResidentIDNumber.validate('440524188001010014'))
        self.assertTrue(CHN.ResidentIDNumber.validate('11010519491231002X'))

    def test_error_case(self):
        self.assertFalse(CHN.ResidentIDNumber.validate('11010219840506970X'))
        self.assertFalse(CHN.ResidentIDNumber.validate('440524189001010014'))
        self.assertFalse(CHN.ResidentIDNumber.validate('11020519491231002X'))

    def test_parse(self):
        result = CHN.ResidentIDNumber.parse('11010219840406970X')
        self.assertEqual('110102', result['address_code'])
        self.assertEqual(1984, result['yyyymmdd'].year)
        self.assertEqual(4, result['yyyymmdd'].month)
        self.assertEqual(6, result['yyyymmdd'].day)
        self.assertEqual('970', result['sn'])
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('X', result['checksum'])

        result = CHN.ResidentIDNumber.parse('440524188001010014')
        self.assertEqual('440524', result['address_code'])
        self.assertEqual(1880, result['yyyymmdd'].year)
        self.assertEqual(1, result['yyyymmdd'].month)
        self.assertEqual(1, result['yyyymmdd'].day)
        self.assertEqual('001', result['sn'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual(4, result['checksum'])


if __name__ == '__main__':
    main()
