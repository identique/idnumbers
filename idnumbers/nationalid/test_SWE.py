from unittest import TestCase, main
from .constant import Gender

from idnumbers.nationalid import SWE


class TestSWEValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(SWE.PersonalIdentityNumber.validate('850709-9805'))
        self.assertTrue(SWE.PersonalIdentityNumber.validate('191231+2392'))

    def test_error_case(self):
        self.assertFalse(SWE.PersonalIdentityNumber.validate('850709-9802'))
        self.assertFalse(SWE.PersonalIdentityNumber.validate('191231+2391'))
        self.assertFalse(SWE.PersonalIdentityNumber.validate('850709_9805'))
        self.assertFalse(SWE.PersonalIdentityNumber.validate('850709 _ 9805'))

    def test_parse(self):
        result = SWE.PersonalIdentityNumber.parse('850709-9805')
        self.assertEqual(1985, result['yyyymmdd'].year)
        self.assertEqual(7, result['yyyymmdd'].month)
        self.assertEqual(9, result['yyyymmdd'].day)
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('5', result['checksum'])


if __name__ == '__main__':
    main()
