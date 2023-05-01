from unittest import TestCase

from idnumbers.nationalid.CYP import TIN


class TestCYPTaxNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(TIN.individual.validate('00123123T'))
        self.assertTrue(TIN.individual.validate('99652156X'))

    def test_error_case(self):
        self.assertFalse(TIN.individual.validate('00123123A'))
        self.assertFalse(TIN.individual.validate('99652156B'))
