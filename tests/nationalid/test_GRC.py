from unittest import TestCase

from idnumbers import registry
from idnumbers.nationalid import GRC


class TestGRCNationalInsuranceNumberValidation(TestCase):
    def test_identity_card_significant_lengths_and_layouts(self):
        for cls, length, layouts in (
            (GRC.IdentityCard, 8, ("AB123456", "AB-123456")),
            (GRC.OldIdentityCard, 7, ("Α123456", "Α-123456")),
        ):
            with self.subTest(card=cls.__name__):
                self.assertEqual(length, cls.METADATA.min_length)
                self.assertEqual(length, cls.METADATA.max_length)
                for value in layouts:
                    self.assertTrue(cls.validate(value))
                    self.assertEqual(length, len(value.replace("-", "")))
                self.assertEqual(length + 1, len(layouts[1]))

    def test_normal_case(self):
        self.assertTrue(GRC.OldIdentityCard.validate("Φ-123456"))
        self.assertTrue(GRC.IdentityCard.validate("ΦA-123456"))
        self.assertTrue(GRC.TaxIdentityNumber.validate("355827182"))

    def test_error_case(self):
        self.assertFalse(GRC.OldIdentityCard.validate("A-123456"))  # test with latin
        self.assertFalse(GRC.IdentityCard.validate("A-123456"))  # wrong digits
        self.assertFalse(GRC.TaxIdentityNumber.validate("355827181"))

    def test_tin_namespace(self):
        self.assertIs(GRC.TIN.individual, GRC.TaxIdentityNumber)
        self.assertIs(GRC.TIN.entity, GRC.TaxIdentityNumber)
        invalid_values = (
            "355827181",
            "35582718A",
            "35582718",
            "3558271820",
            "355827182\n",
            "٣55827182",
            "",
            None,
            355827182,
        )
        for taxpayer_type in (GRC.TIN.individual, GRC.TIN.entity):
            with self.subTest(taxpayer_type=taxpayer_type):
                self.assertTrue(taxpayer_type.validate("355827182"))
                for value in invalid_values:
                    with self.subTest(value=value):
                        self.assertFalse(taxpayer_type.validate(value))

    def test_national_id_and_registry_primary_remain_identity_card(self):
        self.assertIs(GRC.NationalID.METADATA.alias_of, GRC.IdentityCard)
        self.assertTrue(GRC.NationalID.validate(GRC.IdentityCard.METADATA.example))
        self.assertFalse(GRC.NationalID.validate("355827182"))
        entry = registry.get_country("GRC")
        assert entry is not None
        self.assertIs(entry.national_id, GRC.NationalID)
        self.assertIs(registry.get_validator("GRC"), GRC.NationalID)
        self.assertNotIn(GRC.TIN, entry.id_types)
