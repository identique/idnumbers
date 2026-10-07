from unittest import TestCase, main
from idnumbers.nationalid import IRL


def _check_char_for_suffix(digits, suffix):
    """Compute the current (non-legacy) weighted check character independently."""
    weighted_sum = sum(int(digit) * weight for digit, weight in zip(digits, (8, 7, 6, 5, 4, 3, 2)))
    weighted_sum += (ord(suffix) - ord('A') + 1) * 9
    remainder = weighted_sum % 23
    return 'W' if remainder == 0 else chr(ord('A') + remainder - 1)


class TestIRLPPSValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(IRL.PersonalPublicServiceNumber.validate('1234567FA'))
        self.assertTrue(IRL.PersonalPublicServiceNumber.validate('1234567F/A'))
        self.assertTrue(IRL.PersonalPublicServiceNumber.validate('1234567T'))
        self.assertTrue(IRL.PersonalPublicServiceNumber.validate('1234567T '))
        self.assertTrue(IRL.PersonalPublicServiceNumber.validate('1234567TW'))

    def test_supported_suffixes_and_layouts(self):
        # A, B and H are weighted; W and a space are ignored. The slash is optional.
        valid_numbers = (
            ('1234567FA', '1234567F/A'),
            ('1234567OB', '1234567O/B'),
            ('1234567WH', '1234567W/H'),
            ('1234567TW', '1234567T/W'),
            ('1234567T ', '1234567T/ '),
            ('1234567T', '1234567T/'),
        )
        invalid_checksums = (
            ('1234567GA', '1234567G/A'),
            ('1234567PB', '1234567P/B'),
            ('1234567VH', '1234567V/H'),
            ('1234567UW', '1234567U/W'),
            ('1234567U ', '1234567U/ '),
            ('1234567U', '1234567U/'),
        )

        for plain, slash in valid_numbers:
            with self.subTest(number=plain):
                self.assertTrue(IRL.PersonalPublicServiceNumber.validate(plain))
            if slash is not None:
                with self.subTest(number=slash):
                    self.assertTrue(IRL.PersonalPublicServiceNumber.validate(slash))

        for plain, slash in invalid_checksums:
            with self.subTest(number=plain):
                self.assertFalse(IRL.PersonalPublicServiceNumber.validate(plain))
            if slash is not None:
                with self.subTest(number=slash):
                    self.assertFalse(IRL.PersonalPublicServiceNumber.validate(slash))

    def test_other_suffix_letters_are_rejected_even_with_a_valid_check_character(self):
        # 6241365HQ has a correct check character under the current weighted rule,
        # but Q is not an issued PPS suffix. The slash form must also be rejected.
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('6241365HQ'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('6241365H/Q'))

        # Exercise each other formerly accepted suffix using a check character
        # computed directly from the published 8-7-6-5-4-3-2-9 weighting.
        for suffix in 'ABCDEFGHIJKLMNOPQRSTUVW':
            if suffix in 'ABHTW':
                continue
            check_char = _check_char_for_suffix('1234567', suffix)
            for number in ('1234567' + check_char + suffix,
                           '1234567' + check_char + '/' + suffix):
                with self.subTest(number=number):
                    self.assertFalse(IRL.PersonalPublicServiceNumber.validate(number))

    def test_legacy_t_x_suffixes_remain_deferred(self):
        # These legacy-suffix examples are intentionally not added here; their
        # checksum behavior is a separate decision tracked in issue #433.
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('6433435FT'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('6433435FX'))

    def test_only_ascii_space_is_allowed_after_the_check_character(self):
        for whitespace in ('\t', '\n', '\N{NO-BREAK SPACE}'):
            for number in ('1234567T' + whitespace, '1234567T/' + whitespace):
                with self.subTest(number=number):
                    self.assertFalse(IRL.PersonalPublicServiceNumber.validate(number))

    def test_malformed_input_does_not_raise(self):
        for number in (None, 1234567, '', '1234567T//', '1234567T  '):
            with self.subTest(number=number):
                self.assertFalse(IRL.PersonalPublicServiceNumber.validate(number))

    def test_error_case(self):
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('1234567AA'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('1234567AX'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('1234567XX'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('1234567FAA'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('123456F'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('123456FT'))
        self.assertFalse(IRL.PersonalPublicServiceNumber.validate('123456F//A'))

    def test_with_regex(self):
        self.assertRegex('1234567FA', IRL.PersonalPublicServiceNumber.METADATA.regexp)

    def test_with_metadata(self):
        self.assertIsNotNone(IRL.PersonalPublicServiceNumber.METADATA)


if __name__ == '__main__':
    main()
