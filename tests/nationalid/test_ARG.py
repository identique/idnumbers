from unittest import TestCase, main

from idnumbers.nationalid import ARG


class TestARGValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ARG.NationalID.validate('81.544.670'))

    def test_error_case(self):
        self.assertFalse(ARG.NationalID.validate('12#345.678'))
        self.assertFalse(ARG.NationalID.validate('12.345.6783'))
        self.assertFalse(ARG.NationalID.validate('123.345.673'))

    def test_seven_digit_case(self):
        # Numbers below 10 million have 7 digits (python-stdnum stdnum/ar/dni.py)
        self.assertTrue(ARG.NationalID.validate('5.123.456'))
        self.assertTrue(ARG.NationalID.validate('5123456'))
        self.assertTrue(ARG.NationalID.validate('1.000.000'))
        self.assertTrue(ARG.NationalID.validate('81544670'))

    def test_wrong_length_or_grouping_case(self):
        self.assertFalse(ARG.NationalID.validate('123456'))
        self.assertFalse(ARG.NationalID.validate('123.456'))
        self.assertFalse(ARG.NationalID.validate('512.3456'))
        self.assertFalse(ARG.NationalID.validate('5.123.4567'))
        self.assertFalse(ARG.NationalID.validate('.5.123.456'))
        self.assertFalse(ARG.NationalID.validate('123.456.789'))

    def test_metadata_length(self):
        self.assertEqual(ARG.NationalID.METADATA.min_length, 7)
        self.assertEqual(ARG.NationalID.METADATA.max_length, 8)


if __name__ == '__main__':
    main()
