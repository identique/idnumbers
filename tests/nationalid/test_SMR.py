from unittest import TestCase, main

from idnumbers.nationalid import SMR


class TestSMRValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(SMR.NationalID.validate('123456789'))
        self.assertTrue(SMR.TaxRegistrationNumber.validate('SM12345'))

    def test_error_case(self):
        self.assertFalse(SMR.NationalID.validate('a12345678'))
        self.assertFalse(SMR.TaxRegistrationNumber.validate('Sm12345'))


if __name__ == '__main__':
    main()
