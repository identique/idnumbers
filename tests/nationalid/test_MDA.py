from unittest import TestCase, main
from idnumbers.nationalid import MDA


class TestMDANationalIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(MDA.PersonalCode.validate('1234567890123'))

    def test_error_case(self):
        self.assertFalse(MDA.PersonalCode.validate('123456789012'))
        self.assertFalse(MDA.PersonalCode.validate('1234A67890123'))


if __name__ == '__main__':
    main()
