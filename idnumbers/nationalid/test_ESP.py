from unittest import TestCase, main
from idnumbers.nationalid import ESP


class TestESPNationalIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ESP.NationalID.validate('12345678Z'))
        self.assertTrue(ESP.NationalID.validate('10469226V'))

    def test_error_case(self):
        self.assertFalse(ESP.NationalID.validate('1234567A'))
        self.assertFalse(ESP.NationalID.validate('12345678A'))


if __name__ == '__main__':
    main()
