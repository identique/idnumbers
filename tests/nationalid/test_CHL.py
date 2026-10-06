from unittest import TestCase, main

from idnumbers.nationalid import CHL


class TestCHLNationalIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(CHL.NationalID.validate('28.373.183-9'))
        self.assertTrue(CHL.NationalID.validate('31.174.738-K'))

    def test_seven_digit_body(self):
        # Issue #286: the weights are right-aligned (2,3,4,5,6,7,2,...), so 7-digit bodies use [2,7,6,5,4,3,2]
        # reversed. Sources: es.wikipedia "Rol Único Tributario" and python-stdnum stdnum.cl.rut; the expected
        # check characters were computed with the right-aligned rule.
        self.assertTrue(CHL.NationalID.validate('1.111.111-4'))
        self.assertTrue(CHL.NationalID.validate('6.123.456-K'))
        self.assertEqual(CHL.NationalID.checksum('1.111.111-4'), '4')
        self.assertEqual(CHL.NationalID.checksum('6.123.456-K'), 'K')

    def test_eight_digit_body_checksum(self):
        # Existing vectors and a K case (check character computed with the right-aligned rule).
        self.assertEqual(CHL.NationalID.checksum('28.373.183-9'), '9')
        self.assertEqual(CHL.NationalID.checksum('31.174.738-K'), 'K')
        self.assertEqual(CHL.NationalID.checksum('10.000.013-K'), 'K')

    def test_error_case(self):
        self.assertFalse(CHL.NationalID.validate('130.692.545-9'))
        self.assertFalse(CHL.NationalID.validate('28.373.183-3'))
        self.assertFalse(CHL.NationalID.validate('34.260.389-K'))

    def test_seven_digit_body_error_case(self):
        # Issue #286: these were accepted by the left-aligned weights.
        self.assertFalse(CHL.NationalID.validate('1.111.111-3'))
        self.assertFalse(CHL.NationalID.validate('6.123.456-0'))

    def test_with_metadata(self):
        self.assertIsNotNone(CHL.NationalID.METADATA)
        self.assertTrue(CHL.NationalID.METADATA.checksum)


if __name__ == '__main__':
    main()
