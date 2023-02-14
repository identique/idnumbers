from unittest import TestCase, main

from idnumbers.nationalid import LTU


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


if __name__ == '__main__':
    main()
