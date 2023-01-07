from unittest import TestCase, main
from datetime import date

from idnumbers.nationalid import NOR
from .constant import Gender


class TestNORValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NOR.NationalID.validate('29029600013'))

    def test_error_case(self):
        self.assertFalse(NOR.NationalID.validate('29029600012'))

    def test_parse(self):
        result = NOR.NationalID.parse('29029600013')
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual(date(1996, 2, 29), result['yyyymmdd'])
        self.assertEqual('13', result['checksum'])


if __name__ == '__main__':
    main()
