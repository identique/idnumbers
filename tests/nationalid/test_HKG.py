from unittest import TestCase, main
from idnumbers.nationalid import HKG


class TestHKGValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(HKG.NationalID.validate('TP1490258'))
        self.assertTrue(HKG.NationalID.validate('D360546A'))

    def test_error_case(self):
        self.assertFalse(HKG.NationalID.validate('LL2557369A'))
        self.assertFalse(HKG.NationalID.validate('TP1490253'))

    def test_with_regex(self):
        self.assertRegex('TP1490258', HKG.NationalID.METADATA.regexp)

    def test_with_metadata(self):
        self.assertIsNotNone(HKG.NationalID.METADATA)


if __name__ == '__main__':
    main()
