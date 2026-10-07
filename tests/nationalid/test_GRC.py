from unittest import TestCase

from idnumbers.nationalid import GRC


class TestGRCNationalInsuranceNumberValidation(TestCase):
    def test_identity_card_significant_lengths_and_layouts(self):
        for cls, length, layouts in (
                (GRC.IdentityCard, 8, ('AB123456', 'AB-123456')),
                (GRC.OldIdentityCard, 7, ('Α123456', 'Α-123456'))):
            with self.subTest(card=cls.__name__):
                self.assertEqual(length, cls.METADATA.min_length)
                self.assertEqual(length, cls.METADATA.max_length)
                for value in layouts:
                    self.assertTrue(cls.validate(value))
                    self.assertEqual(length, len(value.replace('-', '')))
                self.assertEqual(length + 1, len(layouts[1]))

    def test_normal_case(self):
        self.assertTrue(GRC.OldIdentityCard.validate('Φ-123456'))
        self.assertTrue(GRC.IdentityCard.validate('ΦA-123456'))
        self.assertTrue(GRC.TaxIdentityNumber.validate('355827182'))

    def test_error_case(self):
        self.assertFalse(GRC.OldIdentityCard.validate('A-123456'))  # test with latin
        self.assertFalse(GRC.IdentityCard.validate('A-123456'))  # wrong digits
        self.assertFalse(GRC.TaxIdentityNumber.validate('355827181'))
