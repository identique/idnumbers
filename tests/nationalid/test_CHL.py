from unittest import TestCase, main

from idnumbers.nationalid import CHL


class TestCHLNationalIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(CHL.NationalID.validate('28.373.183-9'))
        self.assertTrue(CHL.NationalID.validate('31.174.738-K'))

    def test_error_case(self):
        self.assertFalse(CHL.NationalID.validate('130.692.545-9'))
        self.assertFalse(CHL.NationalID.validate('28.373.183-3'))
        self.assertFalse(CHL.NationalID.validate('34.260.389-K'))

    def test_with_metadata(self):
        self.assertIsNotNone(CHL.NationalID.METADATA)
        self.assertTrue(CHL.NationalID.METADATA.checksum)


if __name__ == '__main__':
    main()
