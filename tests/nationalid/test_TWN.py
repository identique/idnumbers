from unittest import TestCase, main

from idnumbers.nationalid import TWN
from idnumbers.nationalid.constant import Gender


class TestTWNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(TWN.NationalID.validate('A123456789'))
        self.assertTrue(TWN.NationalID.validate('M140051653'))
        self.assertTrue(TWN.NationalID.validate('Q238927307'))

    def test_error_case(self):
        self.assertFalse(TWN.NationalID.validate('A223456789'))
        self.assertFalse(TWN.NationalID.validate('m140051653'))

    def test_parse(self):
        result = TWN.NationalID.parse('A123456789')
        self.assertEqual('A', result['location'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('2345678', result['sn'])
        self.assertEqual(9, result['checksum'])

    def test_check_digit_zero(self):
        # M162773050 is the example from issue #276; the A... vectors come from the
        # differential comparison comment on #276 (Node port 2.2.0 accepts them).
        # All satisfy the zh.wikipedia rule: the weighted sum including the check
        # digit is a multiple of 10.
        for id_number in ['A120229780', 'A123402290', 'A130456780', 'M162773050']:
            with self.subTest(id_number=id_number):
                self.assertTrue(TWN.NationalID.validate(id_number))
                self.assertEqual(0, TWN.NationalID.checksum(id_number))
        self.assertEqual(0, TWN.NationalID.parse('A120229780')['checksum'])

    def test_check_digit_zero_wrong_digit(self):
        self.assertFalse(TWN.NationalID.validate('A120229781'))
        self.assertFalse(TWN.NationalID.validate('M162773051'))

    def test_checksum_on_malformed_input(self):
        self.assertIsNone(TWN.NationalID.checksum('abc'))
        self.assertIsNone(TWN.NationalID.checksum(None))
        self.assertIsNone(TWN.NationalID.checksum('a120229780'))


if __name__ == '__main__':
    main()
