from unittest import TestCase, main

from idnumbers.nationalid import PHL


class TestPHLValidation(TestCase):
    def test_psn_metadata_and_existing_layouts(self):
        self.assertEqual(['PhilSys Number', 'PSN', 'Philippine National ID'], PHL.PhilID.METADATA.names)
        self.assertEqual(12, PHL.PhilID.METADATA.min_length)
        self.assertEqual(12, PHL.PhilID.METADATA.max_length)
        self.assertEqual('PhilID', PHL.PhilID.__name__)
        self.assertIs(PHL.PhilID, PHL.NationalID.METADATA.alias_of)
        self.assertIn('12-digit PhilSys Number (PSN)', PHL.PhilID.__doc__)
        self.assertIn('16-digit PhilID Card Number (PCN)', PHL.PhilID.__doc__)
        self.assertIn(
            'https://psa.gov.ph/content/psa-bsp-promote-philid-card-security-and-verification-features',
            PHL.PhilID.METADATA.links)
        # Synthetic format-only vectors; PSA distinguishes the 12-digit PSN from the 16-digit PCN.
        for value in ('123456789123', '1234-5678912-3', '1234 5678912 3',
                      '1234-5678912 3', '1234 5678912-3'):
            with self.subTest(value=value):
                self.assertTrue(PHL.PhilID.validate(value))
                self.assertTrue(PHL.NationalID.validate(value))
                self.assertEqual(12, len(value.replace('-', '').replace(' ', '')))
        for value in ('1234567891234567', '1234-5678-9123-4567'):
            self.assertFalse(PHL.PhilID.validate(value))
            self.assertFalse(PHL.NationalID.validate(value))

    def test_normal_case(self):
        self.assertTrue(PHL.PhilID.validate('1234-5678912-3'))
        self.assertTrue(PHL.PhilID.validate('123456789123'))

    def test_error_case(self):
        self.assertFalse(PHL.PhilID.validate('1234567890'))


if __name__ == '__main__':
    main()
