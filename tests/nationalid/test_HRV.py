from unittest import TestCase, main
from idnumbers.nationalid import HRV


class TestHRVValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(HRV.PersonalID.validate('94577403194'))
        self.assertTrue(HRV.PersonalID.validate('69435151530'))

    def test_error_case(self):
        self.assertFalse(HRV.PersonalID.validate('6943515153'))
        self.assertFalse(HRV.PersonalID.validate('69435151531'))


if __name__ == '__main__':
    main()
