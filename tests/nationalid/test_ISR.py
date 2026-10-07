from unittest import TestCase
from idnumbers.nationalid import ISR


class TestISRValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ISR.NationalID.validate('523656783'))
        self.assertTrue(ISR.NationalID.validate('231740705'))
        self.assertTrue(ISR.NationalID.validate('339677395'))

    def test_error_case(self):
        self.assertFalse(ISR.NationalID.validate('523656782'))

    def test_checksum_has_docstring(self):
        self.assertIsNotNone(ISR.NationalID.checksum.__doc__)

    def test_all_zero_is_not_valid_but_has_a_checksum(self):
        self.assertFalse(ISR.NationalID.validate('000000000'))
        self.assertEqual(ISR.NationalID.checksum('000000000'), 0)

    def test_positive_zero_prefixed_numbers(self):
        # Algorithm probes, not evidence of issued IDs. The second is a python-stdnum 2.2 example:
        # https://github.com/arthurdejong/python-stdnum/blob/2.2/stdnum/il/idnr.py
        for number, check_digit in [('000000018', 8), ('039337423', 3)]:
            with self.subTest(number=number):
                self.assertTrue(ISR.NationalID.validate(number))
                self.assertEqual(ISR.NationalID.checksum(number), check_digit)

    def test_wrong_check_digits(self):
        # Fixed mutations with independently known expected check digits.
        for number, check_digit in [('000000019', 8), ('039337424', 3), ('523656782', 3)]:
            with self.subTest(number=number):
                self.assertFalse(ISR.NationalID.validate(number))
                self.assertEqual(ISR.NationalID.checksum(number), check_digit)

    def test_invalid_format_and_type(self):
        # Shorter forms remain rejected: this validator does not pad or normalize inputs.
        invalid_numbers = [
            None, 0, 18, True, [], {}, b'000000018', '', '18', '39337423',
            '00000000', '0000000000', '0000000018', '03933742-3',
            ' 000000018', '000000018 ', '000000018\n', '000000018\r\n',
            '٠٠٠٠٠٠٠١٨', '０００００００１８', '0000000a8', '0000000\x008',
        ]
        for number in invalid_numbers:
            with self.subTest(number=number):
                self.assertFalse(ISR.NationalID.validate(number))
                self.assertIsNone(ISR.NationalID.checksum(number))
