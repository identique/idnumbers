from unittest import TestCase, main

from idnumbers.nationalid import PHL


class TestPHLValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(PHL.NationalID.validate('1234-5678912-3'))
        self.assertTrue(PHL.NationalID.validate('123456789123'))

    def test_error_case(self):
        self.assertFalse(PHL.NationalID.validate('1234567890'))


if __name__ == '__main__':
    main()
