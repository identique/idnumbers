from unittest import TestCase
from idnumbers.nationalid import IRN


class TestIRNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(IRN.NationalID.validate('472-171992-2'))
        self.assertTrue(IRN.NationalID.validate('4608968882'))
        self.assertTrue(IRN.NationalID.validate('1111111111'))
        self.assertTrue(IRN.NationalID.validate('0939092001'))

    def test_error_case(self):
        self.assertFalse(IRN.NationalID.validate('472-171992-1'))
        self.assertFalse(IRN.NationalID.validate('2130396217'))
        self.assertFalse(IRN.NationalID.validate('0000000001'))
        self.assertFalse(IRN.NationalID.validate('abcd1234'))
