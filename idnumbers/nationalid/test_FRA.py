from unittest import TestCase, main

from .constant import Gender
from idnumbers.nationalid import FRA


class TestFRAValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(FRA.NationalID.validate('255081416802538'))
        self.assertTrue(FRA.NationalID.validate('283209921625930'))
        self.assertTrue(FRA.NationalID.validate('255082a16802597'))

    def test_error_case(self):
        self.assertFalse(FRA.NationalID.validate('180126955222381'))
        self.assertFalse(FRA.NationalID.validate('255082e16802597'))

    def test_parse(self):
        result = FRA.NationalID.parse('255082a16802597')
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('55', result['yy'])
        self.assertEqual('08', result['mm'])
        self.assertEqual('97', result['checksum'])


if __name__ == '__main__':
    main()
