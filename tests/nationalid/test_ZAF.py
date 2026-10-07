from datetime import date
from unittest import TestCase, main
from idnumbers.nationalid import ZAF
from idnumbers.nationalid.constant import Citizenship, Gender


class TestZAFValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ZAF.NationalID.validate('7605300675088'))

    def test_october_birth_date(self):
        # Synthetic Luhn-correct vector, not issued; regression coverage for issue #275.
        number = '9510105000086'
        self.assertTrue(ZAF.NationalID.validate(number))
        self.assertEqual({
            'yyyymmdd': date(1995, 10, 10),
            'sn': '5000',
            'gender': Gender.MALE,
            'citizenship': Citizenship.CITIZEN,
            'checksum': 6,
        }, ZAF.NationalID.parse(number))
        self.assertEqual(6, ZAF.NationalID.checksum(number))
        self.assertFalse(ZAF.NationalID.validate(number[:-1] + '7'))
        self.assertIsNone(ZAF.NationalID.parse(number[:-1] + '7'))

    def test_error_case(self):
        self.assertFalse(ZAF.NationalID.validate('7605300675089'))

    def test_parse(self):
        result = ZAF.NationalID.parse('7605300675088')
        self.assertEqual(1976, result['yyyymmdd'].year)
        self.assertEqual(5, result['yyyymmdd'].month)
        self.assertEqual(30, result['yyyymmdd'].day)
        self.assertEqual('0675', result['sn'])
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])
        self.assertEqual(8, result['checksum'])

    def test_non_numeric_input_is_false(self):
        # examples from issue #314 and the former KNOWN_RAISES entry, all used to raise ValueError
        # (except the newline one)
        for value in ['abc', '80010150090 7', '8001015009087\n', 'xxxxxxxxxxx', ' 207012409184', '-207012409184']:
            with self.subTest(value=value):
                self.assertIs(False, ZAF.NationalID.validate(value))
                self.assertIsNone(ZAF.NationalID.parse(value))

    def test_checksum_on_malformed_input(self):
        self.assertIsNone(ZAF.NationalID.checksum('abc'))
        self.assertIsNone(ZAF.NationalID.checksum('80010150090 7'))
        self.assertIsNone(ZAF.NationalID.checksum(None))

    def test_issue_vector(self):
        # issue #314 vector, python-stdnum 2.2 za.idnr agrees
        self.assertTrue(ZAF.NationalID.validate('8001015009087'))
        self.assertEqual(7, ZAF.NationalID.checksum('8001015009087'))

    def test_with_metadata(self):
        self.assertIsNotNone(ZAF.NationalID.METADATA)
        self.assertTrue(ZAF.NationalID.METADATA.parsable)


if __name__ == '__main__':
    main()
