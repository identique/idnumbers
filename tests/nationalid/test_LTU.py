from datetime import date
from unittest import TestCase, main

from idnumbers.nationalid import LTU
from idnumbers.nationalid.constant import Gender


class TestLTUValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(LTU.PersonalCode.validate('48310031084'))
        self.assertTrue(LTU.PersonalCode.validate('46411231034'))
        self.assertTrue(LTU.PersonalCode.validate('37311221319'))

    def test_error_case(self):
        self.assertFalse(LTU.PersonalCode.validate('48310031083'))

    def test_parse(self):
        result = LTU.PersonalCode.parse('48310031084')
        self.assertEqual(1983, result['yyyymmdd'].year)
        self.assertEqual(10, result['yyyymmdd'].month)
        self.assertEqual(3, result['yyyymmdd'].day)
        self.assertEqual('108', result['sn'])
        self.assertEqual(4, result['checksum'])

    @staticmethod
    def make_code(first_digit, yy, mm, dd, sn='001'):
        # Synthetic fixtures: independent two-pass checksum from the OECD LT TIN sheet.
        prefix = f'{first_digit}{yy:02d}{mm:02d}{dd:02d}{sn}'
        digits = [int(digit) for digit in prefix]
        check_digit = sum(digit * weight for digit, weight in
                          zip(digits, (1, 2, 3, 4, 5, 6, 7, 8, 9, 1))) % 11
        if check_digit == 10:
            check_digit = sum(digit * weight for digit, weight in
                              zip(digits, (3, 4, 5, 6, 7, 8, 9, 1, 2, 3))) % 11
        if check_digit == 10:
            check_digit = 0
        return prefix + str(check_digit)

    def test_century_and_gender_pairs(self):
        # python-stdnum 2.2's LT birth-date decoder uses these century pairs.
        for first_digit, century, gender in (
                (1, 1800, Gender.MALE), (2, 1800, Gender.FEMALE),
                (3, 1900, Gender.MALE), (4, 1900, Gender.FEMALE),
                (5, 2000, Gender.MALE), (6, 2000, Gender.FEMALE),
                (7, 2100, Gender.MALE), (8, 2100, Gender.FEMALE)):
            with self.subTest(first_digit=first_digit):
                code = self.make_code(first_digit, 90, 1, 1, '007')
                expected = {'yyyymmdd': date(century + 90, 1, 1), 'gender': gender,
                            'sn': '007', 'checksum': int(code[-1])}
                self.assertTrue(LTU.PersonalCode.validate(code))
                self.assertEqual(expected, LTU.PersonalCode.parse(code))
                self.assertEqual(expected, LTU.NationalID.parse(code))
                self.assertEqual(int(code[-1]), LTU.PersonalCode.checksum(code))

    def test_fixed_regressions(self):
        # Synthetic checksum-correct vectors, not claims of issued personal codes.
        self.assertEqual('39001010077', self.make_code(3, 90, 1, 1, '007'))
        self.assertEqual({'yyyymmdd': date(1990, 1, 1), 'gender': Gender.MALE,
                          'sn': '007', 'checksum': 7}, LTU.PersonalCode.parse('39001010077'))
        self.assertEqual('50002290013', self.make_code(5, 0, 2, 29))
        self.assertTrue(LTU.PersonalCode.validate('50002290013'))
        self.assertEqual(date(2000, 2, 29), LTU.PersonalCode.parse('50002290013')['yyyymmdd'])
        self.assertEqual('70002290015', self.make_code(7, 0, 2, 29))
        self.assertFalse(LTU.PersonalCode.validate('70002290015'))
        self.assertIsNone(LTU.PersonalCode.parse('70002290015'))
        self.assertEqual(5, LTU.PersonalCode.checksum('70002290015'))

    def test_century_leap_boundaries(self):
        for first_digit in range(1, 9):
            with self.subTest(first_digit=first_digit):
                code = self.make_code(first_digit, 0, 2, 29)
                self.assertEqual(int(code[-1]), LTU.PersonalCode.checksum(code))
                if first_digit in (5, 6):
                    self.assertTrue(LTU.PersonalCode.validate(code))
                    self.assertEqual(date(2000, 2, 29), LTU.PersonalCode.parse(code)['yyyymmdd'])
                else:
                    self.assertFalse(LTU.PersonalCode.validate(code))
                    self.assertIsNone(LTU.PersonalCode.parse(code))

    def test_calendar_boundaries(self):
        for first_digit in range(1, 9):
            century = (1800, 1800, 1900, 1900, 2000, 2000, 2100, 2100)[first_digit - 1]
            for yy, mm, dd, valid in (
                    (4, 2, 29, True), (1, 2, 29, False), (1, 1, 31, True),
                    (1, 0, 1, False), (1, 13, 1, False), (1, 1, 0, False),
                    (1, 1, 32, False), (1, 4, 31, False)):
                with self.subTest(first_digit=first_digit, yy=yy, mm=mm, dd=dd):
                    code = self.make_code(first_digit, yy, mm, dd)
                    self.assertEqual(int(code[-1]), LTU.PersonalCode.checksum(code))
                    self.assertEqual(valid, LTU.PersonalCode.validate(code))
                    result = LTU.PersonalCode.parse(code)
                    if valid:
                        self.assertEqual(date(century + yy, mm, dd), result['yyyymmdd'])
                    else:
                        self.assertIsNone(result)

    def test_zero_and_nine_compatibility(self):
        # Keep historical behavior until the separate first-digit policy issue #337 is resolved.
        for first_digit, century, gender in ((0, 1700, Gender.FEMALE), (9, 2100, Gender.MALE)):
            for yy, mm, dd in ((0, 1, 1), (4, 2, 29), (99, 12, 31)):
                with self.subTest(first_digit=first_digit, yy=yy, mm=mm, dd=dd):
                    code = self.make_code(first_digit, yy, mm, dd)
                    self.assertTrue(LTU.PersonalCode.validate(code))
                    self.assertEqual({'yyyymmdd': date(century + yy, mm, dd), 'gender': gender,
                                      'sn': '001', 'checksum': int(code[-1])}, LTU.PersonalCode.parse(code))
            code = self.make_code(first_digit, 0, 2, 29)
            self.assertFalse(LTU.PersonalCode.validate(code))
            self.assertIsNone(LTU.PersonalCode.parse(code))
            self.assertEqual(int(code[-1]), LTU.PersonalCode.checksum(code))

    def test_malformed_input(self):
        code = '39001010077'
        wrong_checksum = code[:-1] + str((int(code[-1]) + 1) % 10)
        self.assertEqual(7, LTU.PersonalCode.checksum(wrong_checksum))
        for invalid in (wrong_checksum, None, 39001010077, False, [], {}, b'39001010077',
                        '', code[:-1], code + '0', code + '\n', code + '\r\n',
                        code.translate(str.maketrans('0123456789', '０１２３４５６７８９')),
                        code.translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))):
            with self.subTest(invalid=invalid):
                self.assertFalse(LTU.PersonalCode.validate(invalid))
                self.assertIsNone(LTU.PersonalCode.parse(invalid))


if __name__ == '__main__':
    main()
