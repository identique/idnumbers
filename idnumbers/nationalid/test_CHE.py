from unittest import TestCase, main

from idnumbers.nationalid import CHE


class TestCHEAVHValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(CHE.SocialSecurityNumber.validate('756.1234.5678.97'))

    def test_error_case(self):
        self.assertFalse(CHE.SocialSecurityNumber.validate('756.1234.5678.90'))
        self.assertFalse(CHE.SocialSecurityNumber.validate('755.1234.5678.90'))
        self.assertFalse(CHE.SocialSecurityNumber.validate('755.1234567897'))


class TestCHEUIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(CHE.UID.validate('CHE-116.281.710'))
        self.assertTrue(CHE.UID.validate('CHE116281710'))

    def test_error_case(self):
        self.assertFalse(CHE.UID.validate('CHE.116.281.710'))
        self.assertFalse(CHE.UID.validate('116.281.710'))


if __name__ == '__main__':
    main()
