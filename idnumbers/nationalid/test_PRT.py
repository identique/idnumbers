from unittest import TestCase, main

from idnumbers.nationalid import PRT


class TestPRTCivilIDNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(PRT.CivilIDNumber.validate('900000007'))
        self.assertTrue(PRT.CivilIDNumber.validate('118666070'))
        self.assertTrue(PRT.TaxIDNumber.validate('100000002'))

    def test_error_case(self):
        self.assertFalse(PRT.CivilIDNumber.validate('900000017'))
        self.assertFalse(PRT.CivilIDNumber.validate('11866607-0'))
        self.assertFalse(PRT.TaxIDNumber.validate('950000002'))


if __name__ == '__main__':
    main()
