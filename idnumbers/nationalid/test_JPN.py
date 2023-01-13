from unittest import TestCase, main
from idnumbers.nationalid import JPN


class TestJPNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(JPN.NationalID.validate('765895492872'))

    def test_error_case(self):
        self.assertFalse(JPN.NationalID.validate('123456789012'))
        self.assertFalse(JPN.NationalID.validate('1234567890123'))

    def test_with_regex(self):
        self.assertRegex('765895492872', JPN.NationalID.METADATA.regexp)

    def test_with_metadata(self):
        self.assertIsNotNone(JPN.NationalID.METADATA)


if __name__ == '__main__':
    main()
