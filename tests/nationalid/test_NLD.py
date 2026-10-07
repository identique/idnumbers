from unittest import TestCase, main

from idnumbers.nationalid import NLD


class TestNLDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NLD.NationalID.validate('1234.56.782'))
        self.assertTrue(NLD.NationalID.validate('1112.22.333'))

    def test_error_case(self):
        self.assertFalse(NLD.NationalID.validate('1234#56.792'))
        self.assertFalse(NLD.NationalID.validate('12.345.6783'))
        self.assertFalse(NLD.NationalID.validate('0000.00.000'))

    def test_compact_and_dotted_checksum_pairs(self):
        # Synthetic vectors verified by the RvIG 11-proof, not issued personal IDs.
        for compact in ('123456782', '111222333', '012345672'):
            dotted = compact[:4] + '.' + compact[4:6] + '.' + compact[6:]
            with self.subTest(compact=compact):
                self.assertTrue(NLD.NationalID.validate(compact))
                self.assertTrue(NLD.NationalID.validate(dotted))
                self.assertIs(NLD.NationalID.checksum(compact), True)
                self.assertIs(NLD.NationalID.checksum(dotted), True)
            wrong = compact[:-1] + str((int(compact[-1]) + 1) % 10)
            wrong_dotted = wrong[:4] + '.' + wrong[4:6] + '.' + wrong[6:]
            with self.subTest(wrong=wrong):
                self.assertFalse(NLD.NationalID.validate(wrong))
                self.assertFalse(NLD.NationalID.validate(wrong_dotted))
                self.assertIs(NLD.NationalID.checksum(wrong), False)
                self.assertIs(NLD.NationalID.checksum(wrong_dotted), False)

    def test_all_zero_rejected_without_changing_checksum(self):
        for value in ('000000000', '0000.00.000'):
            with self.subTest(value=value):
                self.assertFalse(NLD.NationalID.validate(value))
                self.assertIs(NLD.NationalID.checksum(value), True)

    def test_remainder_ten_has_no_valid_check_digit(self):
        # Prefix 00000005 has weighted sum 10, which cannot be a decimal check digit.
        for digit in range(10):
            compact = '00000005' + str(digit)
            dotted = compact[:4] + '.' + compact[4:6] + '.' + compact[6:]
            for value in (compact, dotted):
                with self.subTest(value=value):
                    self.assertFalse(NLD.NationalID.validate(value))
                    self.assertIs(NLD.NationalID.checksum(value), False)

    def test_deterministic_eleven_proof_oracle(self):
        # Independent RvIG LO BSN 2024.Q1, p. 31, footnote 22:
        # 9*s0 + 8*s1 + ... + 2*s7 - s8 must be divisible by 11.
        prefixes = (0, 1, 5, 1234567, 12345678, 11122233, 99999999)
        prefixes += tuple(range(0, 100000000, 999983))
        for prefix in prefixes:
            for digit in range(10):
                compact = '{:08d}{}'.format(prefix, digit)
                total = sum(int(char) * weight for char, weight in
                            zip(compact, (9, 8, 7, 6, 5, 4, 3, 2, -1)))
                expected_checksum = total % 11 == 0
                expected_validity = expected_checksum and compact != '000000000'
                dotted = compact[:4] + '.' + compact[4:6] + '.' + compact[6:]
                for value in (compact, dotted):
                    with self.subTest(value=value):
                        self.assertIs(NLD.NationalID.checksum(value), expected_checksum)
                        self.assertIs(NLD.NationalID.validate(value), expected_validity)

    def test_malformed_inputs(self):
        invalid = (
            '', '1234.56782', '123456.782', '123.456.782', '12345.6.782',
            '1234..56.782', '1234.56..782', '1234-56-782', '1234 56 782',
            ' 123456782', '123456782 ', '\t123456782', '123456782\n',
            '1234.56.782\n', '123456782x', '1234.56.782x',
            '12345678', '1234567820', '123.45.672',
            '１２３４５６７８２', '١٢٣٤٥٦٧٨٢', '１２３４.５６.７８２', '١٢٣٤.٥٦.٧٨٢',
            None, 123456782, b'123456782', [], {}, True,
        )
        for value in invalid:
            with self.subTest(value=value):
                self.assertIs(NLD.NationalID.validate(value), False)


if __name__ == '__main__':
    main()
