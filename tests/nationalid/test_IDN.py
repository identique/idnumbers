from unittest import TestCase, main

from idnumbers.nationalid import IDN


class TestIDNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(IDN.NationalID.validate('7105100607610439'))
        self.assertTrue(IDN.NationalID.validate('7105102902040439'))

    def test_error_case(self):
        self.assertFalse(IDN.NationalID.validate('7105102902020439'))
        self.assertFalse(IDN.NationalID.validate('0950060607610439'))
        self.assertFalse(IDN.NationalID.validate('7105101613610439'))
        self.assertFalse(IDN.NationalID.validate('7105100607610000'))

    def test_parse(self):
        result = IDN.NationalID.parse('7105100607610439')
        self.assertEqual("06", result['dd'])
        self.assertEqual("07", result['mm'])
        self.assertEqual("61", result['yy'])


if __name__ == '__main__':
    main()
