from unittest import TestCase, main

from idnumbers.nationalid import IND


class TestSGPValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(IND.NationalID.validate('8924 7352 8038'))
        self.assertTrue(IND.NationalID.validate('3977 8800 0234'))
        self.assertTrue(IND.NationalID.validate('5485-5000-8800'))
        self.assertTrue(IND.NationalID.validate('475587669949'))

    def test_error_case(self):
        self.assertFalse(IND.NationalID.validate('47558'))
        self.assertFalse(IND.NationalID.validate('475587669940'))
        self.assertFalse(IND.NationalID.validate('175587669949'))


if __name__ == '__main__':
    main()
