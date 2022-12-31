from unittest import TestCase, main
from idnumbers.nationalid import IRL


class TestIRLPPSValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(IRL.PersonalPublicServiceNumber.validate('1234567FA'))
        self.assertTrue(IRL.PersonalPublicServiceNumber.validate('1234567F/A'))
        self.assertTrue(IRL.PersonalPublicServiceNumber.validate('1234567T'))
        self.assertTrue(IRL.PersonalPublicServiceNumber.validate('1234567T '))
        self.assertTrue(IRL.PersonalPublicServiceNumber.validate('1234567TW'))

    def test_error_case(self):
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('1234567AA'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('1234567AX'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('1234567XX'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('1234567FAA'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('123456F'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('123456FT'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('123456F//A'))

    def test_with_regex(self):
        self.assertRegex('1234567FA', IRL.PersonalPublicServiceNumber.METADATA.regexp)

    def test_with_metadata(self):
        self.assertIsNotNone(IRL.PersonalPublicServiceNumber.METADATA)


if __name__ == '__main__':
    main()
