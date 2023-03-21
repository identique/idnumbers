from unittest import TestCase
from idnumbers.nationalid import ISR


class TestISRValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ISR.NationalID.validate('523656783'))
        self.assertTrue(ISR.NationalID.validate('231740705'))
        self.assertTrue(ISR.NationalID.validate('339677395'))

    def test_error_case(self):
        self.assertFalse(ISR.NationalID.validate('523656782'))
