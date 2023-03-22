from unittest import TestCase
from idnumbers.nationalid import IRQ


class TestIRQValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(IRQ.NationalID.validate('123456789012'))

    def test_error_case(self):
        self.assertFalse(IRQ.NationalID.validate('12345678901'))
