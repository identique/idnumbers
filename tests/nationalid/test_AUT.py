from unittest import TestCase
from idnumbers.nationalid import AUT


class TestAUTValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(AUT.TaxIDNumber.validate('931736581'))

    def test_error_case(self):
        self.assertFalse(AUT.TaxIDNumber.validate('931736580'))
