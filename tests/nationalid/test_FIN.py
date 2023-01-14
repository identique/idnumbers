from unittest import TestCase, main

from idnumbers.nationalid import FIN
from idnumbers.nationalid.constant import Gender


class TestKORValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(FIN.PersonalIdentityCode.validate('131052-308T'))
        self.assertTrue(FIN.PersonalIdentityCode.validate('240147-632T'))
        self.assertTrue(FIN.PersonalIdentityCode.validate('280378-999U'))

    def test_error_case(self):
        self.assertFalse(FIN.PersonalIdentityCode.validate('131052-308t'))
        self.assertFalse(FIN.PersonalIdentityCode.validate('131052-308A'))

    def test_parse(self):
        result = FIN.PersonalIdentityCode.parse('131052-308T')
        self.assertEqual(1952, result['yyyymmdd'].year)
        self.assertEqual(10, result['yyyymmdd'].month)
        self.assertEqual(13, result['yyyymmdd'].day)
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('308', result['sn'])
        self.assertEqual('T', result['checksum'])


if __name__ == '__main__':
    main()
