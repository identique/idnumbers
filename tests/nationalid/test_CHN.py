from unittest import TestCase, main

from idnumbers.nationalid import CHN
from idnumbers.nationalid.constant import Gender


class TestCHNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(CHN.ResidentID.validate('11010219840406970X'))
        self.assertTrue(CHN.ResidentID.validate('440524188001010014'))
        self.assertTrue(CHN.ResidentID.validate('11010519491231002X'))

    def test_error_case(self):
        self.assertFalse(CHN.ResidentID.validate('11010219840506970X'))
        self.assertFalse(CHN.ResidentID.validate('440524189001010014'))
        self.assertFalse(CHN.ResidentID.validate('11020519491231002X'))

    def test_lowercase_check_character(self):
        # Existing test vectors, with only the final check character's case changed.
        for cls in (CHN.ResidentID, CHN.NationalID):
            for number in ('11010219840406970X', '11010519491231002X'):
                with self.subTest(cls=cls.__name__, number=number):
                    self.assertTrue(cls.validate(number))
                    self.assertTrue(cls.validate(number.lower()))
                    self.assertEqual(cls.parse(number), cls.parse(number.lower()))
                    self.assertEqual('X', cls.parse(number.lower())['checksum'])
                    self.assertEqual('X', cls.checksum(number.lower()))

    def test_numeric_check_character_unchanged(self):
        for cls in (CHN.ResidentID, CHN.NationalID):
            with self.subTest(cls=cls.__name__):
                self.assertTrue(cls.validate('440524188001010014'))
                result = cls.parse('440524188001010014')
                self.assertEqual(4, result['checksum'])
                self.assertIs(type(result['checksum']), int)
                self.assertEqual(4, cls.checksum('440524188001010014'))

    def test_incorrect_lowercase_check_character(self):
        for cls in (CHN.ResidentID, CHN.NationalID):
            with self.subTest(cls=cls.__name__):
                self.assertFalse(cls.validate('11010219840506970x'))
                self.assertIsNone(cls.parse('11010219840506970x'))
                # checksum() calculates the expected character; it does not validate it.
                self.assertEqual(1, cls.checksum('11010219840506970x'))

    def test_impossible_dates_with_correct_lowercase_checksum(self):
        # Synthetic arithmetic-correct vectors, not claims of real-world issuance.
        numbers = ('11010219840230004x', '11010200000406003x', '11010219000229000x')
        for cls in (CHN.ResidentID, CHN.NationalID):
            for number in numbers:
                with self.subTest(cls=cls.__name__, number=number):
                    self.assertFalse(cls.validate(number))
                    self.assertIsNone(cls.parse(number))
                    # Calendar validation belongs to parse(), not checksum().
                    self.assertEqual('X', cls.checksum(number))
                    self.assertEqual(cls.checksum(number.upper()), cls.checksum(number))

    def test_malformed_inputs(self):
        number = '11010219840406970x'
        invalid = (
            None, False, 110102198404069700, [], {}, number.encode(), '',
            number[:-1], number + 'x', number + '\n', '\n' + number,
            ' ' + number, number + ' ', number[:6] + ' ' + number[7:],
            number[:-1] + 'ｘ', number[:-1] + 'х', number[:-1] + '×',
            '１' + number[1:], '١' + number[1:], 'X' + number[1:],
        )
        for cls in (CHN.ResidentID, CHN.NationalID):
            for value in invalid:
                with self.subTest(cls=cls.__name__, value=value):
                    self.assertFalse(cls.validate(value))
                    self.assertIsNone(cls.parse(value))
                    self.assertIsNone(cls.checksum(value))

    def test_region_policy_unchanged(self):
        # Synthetic vector: region/issuance policy is deferred to issue #451.
        for cls in (CHN.ResidentID, CHN.NationalID):
            with self.subTest(cls=cls.__name__):
                self.assertTrue(cls.validate('170102198404069700'))
                self.assertEqual('170102', cls.parse('170102198404069700')['address_code'])
                self.assertEqual(0, cls.checksum('170102198404069700'))

    def test_parse(self):
        result = CHN.ResidentID.parse('11010219840406970X')
        self.assertEqual('110102', result['address_code'])
        self.assertEqual(1984, result['yyyymmdd'].year)
        self.assertEqual(4, result['yyyymmdd'].month)
        self.assertEqual(6, result['yyyymmdd'].day)
        self.assertEqual('970', result['sn'])
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('X', result['checksum'])

        result = CHN.ResidentID.parse('440524188001010014')
        self.assertEqual('440524', result['address_code'])
        self.assertEqual(1880, result['yyyymmdd'].year)
        self.assertEqual(1, result['yyyymmdd'].month)
        self.assertEqual(1, result['yyyymmdd'].day)
        self.assertEqual('001', result['sn'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual(4, result['checksum'])


if __name__ == '__main__':
    main()
