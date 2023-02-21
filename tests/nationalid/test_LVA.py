from unittest import TestCase, main

from idnumbers.nationalid import LVA


class TestLVAValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(LVA.get_validator('290156-11605').validate('290156-11605'))
        self.assertTrue(LVA.get_validator('323691-93794').validate('323691-93794'))

    def test_error_case(self):
        self.assertFalse(LVA.PersonalCode.validate('290156-11607'))

    def test_parse(self):
        result = LVA.OldPersonalCode.parse('290156-11605')
        self.assertEqual(1956, result['yyyymmdd'].year)
        self.assertEqual(1, result['yyyymmdd'].month)
        self.assertEqual(29, result['yyyymmdd'].day)
        self.assertEqual('160', result['sn'])
        self.assertEqual(5, result['checksum'])
        self.assertIsNone(LVA.OldPersonalCode.parse('323691-93794'))


if __name__ == '__main__':
    main()
