from unittest import TestCase, main

from idnumbers.nationalid import ROU
from idnumbers.nationalid.constant import Citizenship, Gender


class TestROUValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ROU.PersonalNumericalCode.validate('1800101221144'))
        self.assertTrue(ROU.PersonalNumericalCode.validate('1891113341181'))
        self.assertTrue(ROU.PersonalNumericalCode.validate('1831211379814'))
        self.assertTrue(ROU.PersonalNumericalCode.validate('2891202133223'))

    def test_error_case(self):
        self.assertFalse(ROU.PersonalNumericalCode.validate('1800101221143'))

    def test_parse(self):
        result = ROU.PersonalNumericalCode.parse('1800101221144')
        self.assertEqual(1980, result['yyyymmdd'].year)
        self.assertEqual(1, result['yyyymmdd'].month)
        self.assertEqual(1, result['yyyymmdd'].day)
        self.assertEqual('22', result['location'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])
        self.assertEqual('114', result['sn'])
        self.assertEqual(4, result['checksum'])


if __name__ == '__main__':
    main()
