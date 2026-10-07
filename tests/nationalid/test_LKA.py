from datetime import date, timedelta
from unittest import TestCase, main

from idnumbers.nationalid import LKA
from idnumbers.nationalid.constant import Gender, Citizenship


class TestLKAValidation(TestCase):
    @staticmethod
    def make_new_id(year, days, serial='0123'):
        # Synthetic fixtures: calculate the existing checksum independently of library helpers.
        prefix = f'{year:04d}{days:03d}{serial}'
        weights = (8, 4, 3, 2, 7, 6, 5, 7, 4, 3, 2)
        total = sum(int(digit) * weight for digit, weight in zip(prefix, weights))
        return prefix + str((11 - total % 11) % 10)

    def test_normal_case(self):
        self.assertTrue(LKA.NationalID.validate('198713001450'))
        self.assertTrue(LKA.NationalID.validate('198571700717'))
        self.assertTrue(LKA.NationalID.validate('198732403040'))
        self.assertTrue(LKA.NationalID.validate('200159302029'))
        self.assertTrue(LKA.NationalID.validate('199612003996'))
        self.assertTrue(LKA.NationalID.validate('199234004783'))
        self.assertTrue(LKA.OldNationalID.validate('961203996V'))
        self.assertTrue(LKA.OldNationalID.validate('790930622V'))
        self.assertTrue(LKA.OldNationalID.validate('843020461V'))
        self.assertTrue(LKA.OldNationalID.validate('923404716V'))

    def test_error_case(self):
        self.assertFalse(LKA.NationalID.validate('197419202757'))
        self.assertFalse(LKA.NationalID.validate('19741920275X'))
        self.assertFalse(LKA.OldNationalID.validate('790930622A'))

    def test_parse(self):
        result = LKA.NationalID.parse('200159302029')
        self.assertEqual(2001, result['yyyymmdd'].year)
        self.assertEqual(4, result['yyyymmdd'].month)
        self.assertEqual(3, result['yyyymmdd'].day)
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('0202', result['sn'])
        self.assertEqual(9, result['checksum'])
        # old version
        result = LKA.OldNationalID.parse('923404716V')
        self.assertEqual(1992, result['yyyymmdd'].year)
        self.assertEqual(12, result['yyyymmdd'].month)
        self.assertEqual(5, result['yyyymmdd'].day)
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('0471', result['sn'])
        self.assertEqual(6, result['checksum'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])

    def test_convert(self):
        self.assertEqual('199612003996', LKA.OldNationalID.to_new('961203996V'))

    def test_issue_day_regressions(self):
        for id_type, numbers in (
            (LKA.NationalID, ('199900000018', '199999900011', '199950000016')),
            (LKA.OldNationalID, ('000001236V',)),
        ):
            for number in numbers:
                with self.subTest(number=number):
                    self.assertTrue(id_type.checksum(number))
                    self.assertFalse(id_type.validate(number))
                    self.assertIsNone(id_type.parse(number))
        # Conversion remains syntactic, even when the encoded day is invalid.
        self.assertEqual('190000001236', LKA.OldNationalID.to_new('000001236V'))

    def test_all_encoded_days(self):
        # Sweep leap and nonleap years, including every range boundary, in both formats.
        # Within-range date decoding is deliberately unchanged pending issue #437.
        for year in (1992, 1999):
            for days in range(1000):
                new_id = self.make_new_id(year, days)
                old_prefix = new_id[2:7] + new_id[8:]
                expected_valid = 1 <= days <= 366 or 501 <= days <= 866
                for id_type, number in (
                    (LKA.NationalID, new_id),
                    *((LKA.OldNationalID, old_prefix + suffix) for suffix in ('V', 'v', 'X', 'x')),
                ):
                    with self.subTest(year=year, days=days, number=number):
                        self.assertTrue(id_type.checksum(number))
                        self.assertEqual(expected_valid, id_type.validate(number))
                        result = id_type.parse(number)
                        if not expected_valid:
                            self.assertIsNone(result)
                            if id_type is LKA.OldNationalID:
                                self.assertEqual(new_id, id_type.to_new(number))
                            continue
                        ordinal = days if days <= 366 else days - 500
                        expected = {
                            'yyyymmdd': date(year, 1, 1) + timedelta(days=ordinal - 1),
                            'gender': Gender.MALE if days <= 366 else Gender.FEMALE,
                            'sn': '0123',
                            'checksum': int(new_id[-1]),
                        }
                        if id_type is LKA.OldNationalID:
                            expected['citizenship'] = (
                                Citizenship.CITIZEN if number[-1].upper() == 'V' else Citizenship.RESIDENT
                            )
                            self.assertEqual(new_id, id_type.to_new(number))
                        self.assertEqual(expected, result)

    def test_date_representation_limits(self):
        for year, days, expected_date in (
            (0, 1, None), (1, 1, date(1, 1, 1)), (1, 501, date(1, 1, 1)),
            (9999, 365, date(9999, 12, 31)), (9999, 865, date(9999, 12, 31)),
            (9999, 366, None), (9999, 866, None),
        ):
            number = self.make_new_id(year, days)
            with self.subTest(number=number):
                self.assertTrue(LKA.NationalID.checksum(number))
                self.assertEqual(expected_date is not None, LKA.NationalID.validate(number))
                result = LKA.NationalID.parse(number)
                if expected_date is None:
                    self.assertIsNone(result)
                else:
                    self.assertEqual(expected_date, result['yyyymmdd'])

    def test_wrong_checksum(self):
        for days in (1, 366, 501, 866):
            new_id = self.make_new_id(1992, days)
            wrong_id = new_id[:-1] + str((int(new_id[-1]) + 1) % 10)
            for id_type, number in (
                (LKA.NationalID, wrong_id),
                (LKA.OldNationalID, wrong_id[2:7] + wrong_id[8:] + 'V'),
            ):
                with self.subTest(number=number):
                    self.assertFalse(id_type.checksum(number))
                    self.assertFalse(id_type.validate(number))
                    self.assertIsNone(id_type.parse(number))

    def test_malformed_input(self):
        new_id = self.make_new_id(1992, 501)
        old_id = new_id[2:7] + new_id[8:] + 'V'
        for id_type, valid_id in ((LKA.NationalID, new_id), (LKA.OldNationalID, old_id)):
            fullwidth = valid_id.translate(str.maketrans('0123456789', '０１２３４５６７８９'))
            arabic_indic = valid_id.translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))
            for number in (
                None, 123, True, [], {}, valid_id.encode(), '', fullwidth, arabic_indic,
                valid_id + '\n', valid_id + 'A', ' ' + valid_id, valid_id + ' ',
            ):
                with self.subTest(id_type=id_type, number=number):
                    self.assertFalse(id_type.validate(number))
                    self.assertIsNone(id_type.parse(number))
                    self.assertFalse(id_type.checksum(number))
                    if id_type is LKA.OldNationalID:
                        self.assertIsNone(id_type.to_new(number))


if __name__ == '__main__':
    main()
