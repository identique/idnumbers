from unittest import TestCase

from idnumbers.nationalid import GEO


class TestGEOValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(GEO.PersonalNumber.validate('023456789'))

    def test_error_case(self):
        self.assertFalse(GEO.PersonalNumber.validate('12345678'))
