from unittest import TestCase, main
from idnumbers.nationalid import ZAF
from idnumbers.nationalid.constant import Citizenship, Gender


class TestZAFValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ZAF.NationalID.validate('7605300675088'))

    def test_error_case(self):
        self.assertFalse(ZAF.NationalID.validate('7605300675089'))

    def test_number_type(self):
        # if the user doesn't follow the type hinting, we still handle it
        self.assertTrue(ZAF.NationalID.validate(7605300675088))

    def test_parse(self):
        result = ZAF.NationalID.parse('7605300675088')
        self.assertEqual(1976, result['yyyymmdd'].year)
        self.assertEqual(5, result['yyyymmdd'].month)
        self.assertEqual(30, result['yyyymmdd'].day)
        self.assertEqual('0675', result['sn'])
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])
        self.assertEqual(8, result['checksum'])

    def test_with_metadata(self):
        self.assertIsNotNone(ZAF.NationalID.METADATA)
        self.assertTrue(ZAF.NationalID.METADATA.parsable)


if __name__ == '__main__':
    main()
