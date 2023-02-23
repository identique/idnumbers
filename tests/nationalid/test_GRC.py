from unittest import TestCase

from idnumbers.nationalid import GRC


class TestGRCNationalInsuranceNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(GRC.OldIdentityCard.validate('Φ-123456'))
        self.assertTrue(GRC.IdentityCard.validate('ΦA-123456'))
        self.assertTrue(GRC.TaxIdentityNumber.validate('355827182'))

    def test_error_case(self):
        self.assertFalse(GRC.OldIdentityCard.validate('A-123456'))  # test with latin
        self.assertFalse(GRC.IdentityCard.validate('A-123456'))  # wrong digits
        self.assertFalse(GRC.TaxIdentityNumber.validate('355827181'))
