from unittest import TestCase

from idnumbers.nationalid import KAZ


class TestKAZValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(KAZ.IndividualIDNumber.validate('901123300258'))
        self.assertTrue(KAZ.BusinessIDNumber.validate('990940003030'))

    def test_error_case(self):
        self.assertFalse(KAZ.IndividualIDNumber.validate('901123300255'))
        self.assertFalse(KAZ.BusinessIDNumber.validate('990940003031'))

    def test_parse(self):
        result = KAZ.IndividualIDNumber.parse('901123300258')
        self.assertEqual(1990, result['yyyymmdd'].year)
        self.assertEqual(11, result['yyyymmdd'].month)
        self.assertEqual(23, result['yyyymmdd'].day)
        self.assertEqual('0025', result['sn'])
        self.assertEqual(8, result['checksum'])

        result = KAZ.BusinessIDNumber.parse('990940003030')
        self.assertEqual(99, result['yy'])
        self.assertEqual(9, result['mm'])
        self.assertEqual(KAZ.EntityType.ResidentEntity, result['entity_type'])
        self.assertEqual(KAZ.EntityDivision.HeadUnit, result['entity_division'])
        self.assertEqual('00303', result['sn'])
        self.assertEqual(0, result['checksum'])

    @staticmethod
    def make_bin(month):
        """Build synthetic vectors using the documented two-pass weights independently."""
        for serial in range(100000):
            prefix = f'99{month:02d}40{serial:05d}'
            digits = [int(digit) for digit in prefix]
            check_digit = sum(digit * weight for digit, weight in zip(digits, range(1, 12))) % 11
            if check_digit == 10:
                weights = (3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 2)
                check_digit = sum(digit * weight for digit, weight in zip(digits, weights)) % 11
            if check_digit < 10:
                return prefix + str(check_digit)
        raise AssertionError('No usable checksum for synthetic BIN')

    def test_bin_entity_types(self):
        # Resident regression and issue #297's nonresident/joint-enterprise vectors.
        cases = (
            ('990940003030', KAZ.EntityType.ResidentEntity, 0),
            ('990950003035', KAZ.EntityType.NonResidentEntity, 5),
            ('990960003030', KAZ.EntityType.IP, 0),
        )
        for number, entity_type, check_digit in cases:
            with self.subTest(number=number):
                self.assertTrue(KAZ.BusinessIDNumber.validate(number))
                self.assertEqual({
                    'yy': 99,
                    'mm': 9,
                    'entity_type': entity_type,
                    'entity_division': KAZ.EntityDivision.HeadUnit,
                    'sn': '00303',
                    'checksum': check_digit,
                }, KAZ.BusinessIDNumber.parse(number))

    def test_bin_registration_months(self):
        # All 100 month encodings have a correct check digit; rejection is not vacuous.
        for month in range(100):
            number = self.make_bin(month)
            with self.subTest(month=month, number=number):
                self.assertEqual(int(number[-1]), KAZ.BusinessIDNumber.checksum(number))
                self.assertEqual(1 <= month <= 12, KAZ.BusinessIDNumber.validate(number))
                result = KAZ.BusinessIDNumber.parse(number)
                if 1 <= month <= 12:
                    self.assertIsNotNone(result)
                    self.assertEqual(month, result['mm'])
                    self.assertEqual(99, result['yy'])
                else:
                    self.assertIsNone(result)

    def test_bin_zero_month_issue_vector(self):
        # Issue #297: format and arithmetic checksum are valid, registration month is not.
        number = '750061381659'
        self.assertEqual(9, KAZ.BusinessIDNumber.checksum(number))
        self.assertFalse(KAZ.BusinessIDNumber.validate(number))
        self.assertIsNone(KAZ.BusinessIDNumber.parse(number))

    def test_bin_bad_checksum(self):
        for month in (1, 9, 12):
            number = self.make_bin(month)
            invalid = number[:-1] + str((int(number[-1]) + 1) % 10)
            with self.subTest(number=invalid):
                self.assertFalse(KAZ.BusinessIDNumber.validate(invalid))
                self.assertIsNone(KAZ.BusinessIDNumber.parse(invalid))

    def test_bin_malformed_input(self):
        cases = (
            None, 990940003030, b'990940003030', [], {}, '',
            '99094000303', '9909400030300', '99094000303A',
            ' 990940003030', '990940003030 ', '990940003030\n',
            '９９０９４０００３０３０', '٩٩٠٩٤٠٠٠٣٠٣٠',
            '990930003030', '990944003030',
        )
        for number in cases:
            with self.subTest(number=number):
                self.assertFalse(KAZ.BusinessIDNumber.validate(number))
                self.assertIsNone(KAZ.BusinessIDNumber.parse(number))
