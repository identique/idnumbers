from unittest import TestCase, main

from idnumbers.nationalid import TUR


class TestTURValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(TUR.NationalID.validate('10000000146'))
        self.assertTrue(TUR.NationalID.validate('15973515680'))

    def test_error_case(self):
        self.assertFalse(TUR.NationalID.validate('00000000178'))
        self.assertFalse(TUR.NationalID.validate('10000000145'))


if __name__ == '__main__':
    main()
