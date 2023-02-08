from unittest import TestCase, main
from idnumbers.nationalid import PNG


class TestPNGNationalIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(PNG.NationalID.validate('0211907202'))

    def test_error_case(self):
        self.assertFalse(PNG.NationalID.validate('021190720'))
        self.assertFalse(PNG.NationalID.validate('021A907202'))


if __name__ == '__main__':
    main()
