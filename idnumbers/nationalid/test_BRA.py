from unittest import TestCase, main

from idnumbers.nationalid import BRA


class TestBRARGNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(BRA.RGNumber.validate('39.985.676-6'))
        self.assertTrue(BRA.RGNumber.validate('56.843.539-4'))
        self.assertTrue(BRA.RGNumber.validate('99.953.539-X'))

    def test_error_case(self):
        self.assertFalse(BRA.RGNumber.validate('39.985.676-5'))
        self.assertFalse(BRA.RGNumber.validate('56.843.539-X'))

    def test_with_metadata(self):
        self.assertIsNotNone(BRA.RGNumber.METADATA)
        self.assertTrue(BRA.RGNumber.METADATA.checksum)


class TestBRACPFNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(BRA.CPFNumber.validate('111.333.666-86'))

    def test_error_case(self):
        self.assertFalse(BRA.CPFNumber.validate('111.333.666-81'))

    def test_with_metadata(self):
        self.assertIsNotNone(BRA.CPFNumber.METADATA)
        self.assertTrue(BRA.CPFNumber.METADATA.checksum)


if __name__ == '__main__':
    main()
