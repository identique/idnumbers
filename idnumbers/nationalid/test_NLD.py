from unittest import TestCase, main

from idnumbers.nationalid import NLD


class TestARGValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NLD.NationalID.validate('1234.56.782'))
        self.assertTrue(NLD.NationalID.validate('1112.22.333'))

    def test_error_case(self):
        self.assertFalse(NLD.NationalID.validate('1234#56.792'))
        self.assertFalse(NLD.NationalID.validate('12.345.6783'))
        self.assertFalse(NLD.NationalID.validate('0000.00.000'))


if __name__ == '__main__':
    main()
