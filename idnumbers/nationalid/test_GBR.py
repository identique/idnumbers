from unittest import TestCase, main

from idnumbers.nationalid import GBR


class TestGBRNationalInsuranceNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(GBR.NationalInsuranceNumber.validate('AB123456A'))
        self.assertTrue(GBR.NationalInsuranceNumber.validate('AA012344B'))

    def test_error_case(self):
        self.assertFalse(GBR.NationalInsuranceNumber.validate('AD123456A'))
        self.assertFalse(GBR.NationalInsuranceNumber.validate('BO012344B'))
        self.assertFalse(GBR.NationalInsuranceNumber.validate('GB012344B'))
        self.assertFalse(GBR.NationalInsuranceNumber.validate('AB111111G'))


if __name__ == '__main__':
    main()
