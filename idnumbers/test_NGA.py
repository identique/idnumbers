from unittest import TestCase, main
from . import NGA


class TestNGAValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NGA.validate('12345678901'))

    def test_error_case(self):
        self.assertFalse(NGA.validate('1234567890A'))

    def test_number_type(self):
        # if the user doesn't follow the type hinting, we still handle it
        self.assertTrue(NGA.validate(12345678901))


if __name__ == '__main__':
    main()
