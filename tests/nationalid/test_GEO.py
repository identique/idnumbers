from unittest import TestCase

from idnumbers.nationalid import GEO


class TestGEOValidation(TestCase):
    def test_normal_case(self):
        # 11 digits, may start with 0 (example from issue #292)
        self.assertTrue(GEO.PersonalNumber.validate('01001011234'))
        self.assertTrue(GEO.PersonalNumber.validate('12345678901'))

    def test_error_case(self):
        self.assertFalse(GEO.PersonalNumber.validate('12345678'))

    def test_nine_digits_are_not_a_personal_number(self):
        # 9 digits is a document number or a TIN of a non-citizen or a company
        self.assertFalse(GEO.PersonalNumber.validate('023456789'))
        self.assertFalse(GEO.PersonalNumber.validate('123456789'))

    def test_wrong_length(self):
        self.assertFalse(GEO.PersonalNumber.validate('0100101123'))
        self.assertFalse(GEO.PersonalNumber.validate('010010112345'))

    def test_non_digit_input(self):
        self.assertFalse(GEO.PersonalNumber.validate('0100101123A'))
        self.assertFalse(GEO.PersonalNumber.validate('01001011234\n'))
        # full-width digits
        self.assertFalse(GEO.PersonalNumber.validate('０１００１０１１２３４'))
