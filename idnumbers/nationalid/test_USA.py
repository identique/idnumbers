from unittest import TestCase, main
from idnumbers.nationalid import USA


class TestUSAValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(USA.NationalID.validate('012-12-0928'))

    def test_error_case(self):
        self.assertFalse(USA.NationalID.validate('987-12-0928'))
        self.assertFalse(USA.NationalID.validate('666-12-0000'))

    def test_with_regex(self):
        self.assertRegex('012-12-0928', USA.NationalID.METADATA.regexp)

    def test_with_metadata(self):
        self.assertIsNotNone(USA.NationalID.METADATA)


if __name__ == '__main__':
    main()
