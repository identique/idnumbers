from unittest import TestCase, main
from idnumbers.nationalid import USA


class TestUSAValidation(TestCase):
    def test_significant_length_preserves_required_hyphens(self):
        value = '012-12-0928'  # Existing regression vector, not an issuance assertion.
        self.assertEqual(9, USA.SocialSecurityNumber.METADATA.min_length)
        self.assertEqual(9, USA.SocialSecurityNumber.METADATA.max_length)
        self.assertEqual(11, len(value))
        self.assertTrue(USA.SocialSecurityNumber.validate(value))
        compact = value.replace('-', '')
        self.assertEqual(9, len(compact))
        self.assertFalse(USA.SocialSecurityNumber.validate(compact))

    def test_normal_case(self):
        self.assertTrue(USA.SocialSecurityNumber.validate('012-12-0928'))

    def test_error_case(self):
        self.assertFalse(USA.SocialSecurityNumber.validate('987-12-0928'))
        self.assertFalse(USA.SocialSecurityNumber.validate('666-12-0000'))

    def test_with_regex(self):
        self.assertRegex('012-12-0928', USA.SocialSecurityNumber.METADATA.regexp)

    def test_with_metadata(self):
        self.assertIsNotNone(USA.SocialSecurityNumber.METADATA)


if __name__ == '__main__':
    main()
