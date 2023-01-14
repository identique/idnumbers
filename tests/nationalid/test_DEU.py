from unittest import TestCase, main
from idnumbers.nationalid import DEU


class TestDEUNationalIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(DEU.TaxID.validate('65929970489'))
        self.assertTrue(DEU.TaxID.validate('26954371827'))
        self.assertTrue(DEU.TaxID.validate('86095742719'))

    def test_error_case(self):
        self.assertFalse(DEU.TaxID.validate('65299970480'))
        self.assertFalse(DEU.TaxID.validate('26954371820'))


if __name__ == '__main__':
    main()
