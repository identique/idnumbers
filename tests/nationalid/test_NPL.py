from unittest import TestCase

from idnumbers.nationalid import NPL


class TestNPLValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NPL.NationalID.validate('12345678901'))

    def test_error_case(self):
        self.assertFalse(NPL.NationalID.validate('1234567890'))
