from unittest import TestCase, main

from idnumbers.nationalid import ARG


class TestARGValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ARG.NationalID.validate('81.544.670'))

    def test_error_case(self):
        self.assertFalse(ARG.NationalID.validate('12#345.678'))
        self.assertFalse(ARG.NationalID.validate('12.345.6783'))
        self.assertFalse(ARG.NationalID.validate('123.345.673'))


if __name__ == '__main__':
    main()
