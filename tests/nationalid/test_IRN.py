from unittest import TestCase
from idnumbers.nationalid import IRN


class TestIRNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(IRN.NationalID.validate('472-171992-2'))
        self.assertTrue(IRN.NationalID.validate('4608968882'))
        self.assertTrue(IRN.NationalID.validate('0939092001'))

    def test_error_case(self):
        self.assertFalse(IRN.NationalID.validate('472-171992-1'))
        self.assertFalse(IRN.NationalID.validate('2130396217'))
        self.assertFalse(IRN.NationalID.validate('0000000001'))
        self.assertFalse(IRN.NationalID.validate('abcd1234'))

    @staticmethod
    def accepted_formats(number):
        return (number, f'{number[:3]}-{number[3:9]}-{number[9]}',
                f'{number[:3]}-{number[3:]}', f'{number[:9]}-{number[9]}')

    def test_repeated_digit_numbers_are_rejected(self):
        # Synthetic repeated-digit vectors, excluded by the Persian Tools validator rule.
        for digit in '0123456789':
            for number in self.accepted_formats(digit * 10):
                with self.subTest(number=number):
                    self.assertFalse(IRN.NationalID.validate(number))

    def test_repeated_digit_rule_is_separate_from_checksum(self):
        # These synthetic vectors still have the correct arithmetic check digit.
        for digit in '0123456789':
            for number in self.accepted_formats(digit * 10):
                with self.subTest(number=number):
                    self.assertEqual(IRN.NationalID.checksum(number), int(digit))

    def test_nonrepeated_numbers_keep_supported_formats(self):
        # Existing regression vectors; no claim is made that they were issued to a person.
        for compact in ('4721719922', '4608968882', '0939092001'):
            for number in self.accepted_formats(compact):
                with self.subTest(number=number):
                    self.assertTrue(IRN.NationalID.validate(number))
                    self.assertEqual(IRN.NationalID.checksum(number), int(compact[-1]))

    def test_wrong_check_digits_are_rejected_in_supported_formats(self):
        # Synthetic mutations of the existing valid regression vectors.
        for compact in ('4721719921', '4608968883', '0939092002'):
            for number in self.accepted_formats(compact):
                with self.subTest(number=number):
                    self.assertFalse(IRN.NationalID.validate(number))

    def test_malformed_inputs_do_not_raise(self):
        for number in (None, 4721719922, b'4721719922', [], {}, '', '472171992',
                       '47217199222', '472--171992-2', '47-2171992-2', '472 171992 2',
                       ' 4721719922', '4721719922 ', '4721719922\n',
                       '۴۷۲۱۷۱۹۹۲۲', '４７２１７１９９２２'):
            with self.subTest(number=number):
                self.assertFalse(IRN.NationalID.validate(number))
                self.assertIsNone(IRN.NationalID.checksum(number))
