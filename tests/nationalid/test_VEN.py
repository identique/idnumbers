from unittest import TestCase
from idnumbers.nationalid import VEN


class TestVENValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(VEN.IDCardNumber.validate('V13.150.575'))
        self.assertTrue(VEN.FiscalInformationNumber.validate('V-05892464-0'))
        self.assertTrue(VEN.FiscalInformationNumber.validate('J-07013380-5'))
        self.assertTrue(VEN.FiscalInformationNumber.validate('G-20000041-4'))

    def test_error_case(self):
        self.assertFalse(VEN.IDCardNumber.validate('X13.150.575'))
        self.assertFalse(VEN.FiscalInformationNumber.validate('V-12345678-0'))
