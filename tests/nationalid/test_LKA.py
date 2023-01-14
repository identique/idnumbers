from unittest import TestCase, main

from idnumbers.nationalid import LKA
from idnumbers.nationalid.constant import Gender, Citizenship


class TestLKAValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(LKA.NationalID.validate('198713001450'))
        self.assertTrue(LKA.NationalID.validate('198571700717'))
        self.assertTrue(LKA.NationalID.validate('198732403040'))
        self.assertTrue(LKA.NationalID.validate('200159302029'))
        self.assertTrue(LKA.NationalID.validate('199612003996'))
        self.assertTrue(LKA.NationalID.validate('199234004783'))
        self.assertTrue(LKA.OldNationalID.validate('961203996V'))
        self.assertTrue(LKA.OldNationalID.validate('790930622V'))
        self.assertTrue(LKA.OldNationalID.validate('843020461V'))
        self.assertTrue(LKA.OldNationalID.validate('923404716V'))

    def test_error_case(self):
        self.assertFalse(LKA.NationalID.validate('197419202757'))
        self.assertFalse(LKA.NationalID.validate('19741920275X'))
        self.assertFalse(LKA.OldNationalID.validate('790930622A'))

    def test_parse(self):
        result = LKA.NationalID.parse('200159302029')
        self.assertEqual(2001, result['yyyymmdd'].year)
        self.assertEqual(4, result['yyyymmdd'].month)
        self.assertEqual(3, result['yyyymmdd'].day)
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('0202', result['sn'])
        self.assertEqual(9, result['checksum'])
        # old version
        result = LKA.OldNationalID.parse('923404716V')
        self.assertEqual(1992, result['yyyymmdd'].year)
        self.assertEqual(12, result['yyyymmdd'].month)
        self.assertEqual(5, result['yyyymmdd'].day)
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('0471', result['sn'])
        self.assertEqual(6, result['checksum'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])

    def test_convert(self):
        self.assertEqual('199612003996', LKA.OldNationalID.to_new('961203996V'))


if __name__ == '__main__':
    main()
