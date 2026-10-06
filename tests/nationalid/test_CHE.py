from unittest import TestCase, main

from idnumbers.nationalid import CHE
from idnumbers.nationalid.util import ean13_digit


class TestCHEAVHValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(CHE.SocialSecurityNumber.validate('756.1234.5678.97'))

    def test_ean13_weights_odd_positions_by_1_and_even_by_3(self):
        # 756.9217.0769.85 is the example of python-stdnum's stdnum/ch/ssn.py doctest (EAN-13 check digit 5);
        # 756.2914.1777.64 also validates in python-stdnum 2.2 (ch.ssn.is_valid); issue #285
        self.assertTrue(CHE.SocialSecurityNumber.validate('756.9217.0769.85'))
        self.assertTrue(CHE.SocialSecurityNumber.validate('756.2914.1777.64'))
        self.assertTrue(CHE.AVH.validate('756.9217.0769.85'))
        self.assertTrue(CHE.NationalID.validate('756.2914.1777.64'))

    def test_ean13_invalid_vectors(self):
        # 756.0000.5678.17 only passed with the former weights 1/2 (the right EAN-13 digit is 9), issue #285;
        # 756.9217.0769.84 is the invalid example of python-stdnum's ch/ssn.py doctest
        self.assertFalse(CHE.SocialSecurityNumber.validate('756.0000.5678.17'))
        self.assertTrue(CHE.SocialSecurityNumber.validate('756.0000.5678.19'))
        self.assertFalse(CHE.SocialSecurityNumber.validate('756.9217.0769.84'))

    def test_checksum(self):
        self.assertTrue(CHE.SocialSecurityNumber.checksum('756.9217.0769.85'))
        self.assertFalse(CHE.SocialSecurityNumber.checksum('756.9217.0769.86'))

    def test_separator_before_the_check_digits_must_be_a_dot(self):
        # the regexp had an unescaped '.', so any character got through and normalize() left it in: issue #285
        for value in ('756.1234.5678-97', '756.1234.5678 97', '756.1234.5678x97', '756.1234.567897',
                      '756.1234.5678\n97', '756.1234.5678.97\n'):
            self.assertIs(False, CHE.SocialSecurityNumber.validate(value), repr(value))
            self.assertIs(False, CHE.SocialSecurityNumber.checksum(value), repr(value))
        self.assertTrue(CHE.SocialSecurityNumber.validate('756.1234.5678.97'))

    def test_error_case(self):
        self.assertFalse(CHE.SocialSecurityNumber.validate('756.1234.5678.90'))
        self.assertFalse(CHE.SocialSecurityNumber.validate('755.1234.5678.90'))
        self.assertFalse(CHE.SocialSecurityNumber.validate('755.1234567897'))


class TestEAN13Digit(TestCase):
    def test_known_barcodes(self):
        # real EAN-13 numbers: 978-0-306-40615-7 is the ISBN-13 example of https://en.wikipedia.org/wiki/ISBN,
        # 978-0-471-11709-4 is the EAN-13 example of python-stdnum 2.2 (stdnum/ean.py doctest)
        self.assertEqual(7, ean13_digit([int(char) for char in '978030640615']))
        self.assertEqual(4, ean13_digit([int(char) for char in '978047111709']))

    def test_weights(self):
        # all-ones data: 6 odd positions x 1 + 6 even positions x 3 = 24 -> check digit 6
        self.assertEqual(6, ean13_digit([1] * 12))
        # 12 zeros -> 0
        self.assertEqual(0, ean13_digit([0] * 12))


class TestCHEUIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(CHE.UID.validate('CHE-116.281.710'))
        self.assertTrue(CHE.UID.validate('CHE116281710'))

    def test_error_case(self):
        self.assertFalse(CHE.UID.validate('CHE.116.281.710'))
        self.assertFalse(CHE.UID.validate('116.281.710'))

    def test_check_digit_vectors(self):
        # the issue #285 vectors, validated by python-stdnum 2.2 (ch.uid.is_valid)
        # the weighted sum of 11628171 is 132, 132 % 11 = 0, so the check digit is 0
        # (python-stdnum: (11 - sum) % 11)
        self.assertTrue(CHE.UID.validate('CHE-116.281.710'))
        self.assertFalse(CHE.UID.validate('CHE-116.281.715'))  # wrong check digit
        self.assertFalse(CHE.UID.validate('CHE-126.281.710'))  # wrong check digit
        # CHE-100.155.212 and its invalid neighbour CHE-100.155.213: the doctest of python-stdnum's ch/uid.py
        self.assertTrue(CHE.UID.validate('CHE-100.155.212'))
        self.assertFalse(CHE.UID.validate('CHE-100.155.213'))
        # synthetic: 11628172 gives the check digit 7
        self.assertTrue(CHE.UID.validate('CHE-116.281.727'))
        self.assertFalse(CHE.UID.validate('CHE-116.281.720'))

    def test_check_digit_with_optional_separators(self):
        for value in ('CHE-116.281.710', 'CHE116281710', 'CHE-116281710', 'CHE116.281.710', 'CHE-116.281710'):
            self.assertTrue(CHE.UID.validate(value), value)
            self.assertTrue(CHE.BusinessID.checksum(value), value)
        self.assertFalse(CHE.UID.validate('CHE116281715'))
        self.assertFalse(CHE.BusinessID.checksum('CHE116281715'))

    def test_check_digit_10_is_never_valid(self):
        # synthetic: the weighted sum of the digits 00000003 is 12, 12 % 11 = 1 and 11 - 1 = 10 is not a digit
        for check_digit in range(10):
            value = f'CHE-000.000.03{check_digit}'
            self.assertFalse(CHE.UID.validate(value), value)
            self.assertFalse(CHE.BusinessID.checksum(value), value)

    def test_metadata(self):
        self.assertTrue(CHE.BusinessID.METADATA.checksum)
        # the length is counted without the optional '-' and '.', like the other id types
        stripped = len('CHE116281710')
        self.assertEqual(stripped, CHE.BusinessID.METADATA.min_length)
        self.assertEqual(stripped, CHE.BusinessID.METADATA.max_length)


if __name__ == '__main__':
    main()
