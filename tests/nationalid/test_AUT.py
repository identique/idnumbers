from unittest import TestCase
from idnumbers.nationalid import AUT


class TestAUTValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(AUT.TaxIDNumber.validate('931736581'))

    def test_error_case(self):
        self.assertFalse(AUT.TaxIDNumber.validate('931736580'))

    def test_tin_cases(self):
        self.assertTrue(AUT.TIN.individual.validate('931736581'))
        self.assertTrue(AUT.TIN.entity.validate('U10223006'))
        self.assertFalse(AUT.TIN.entity.validate('U10223007'))
