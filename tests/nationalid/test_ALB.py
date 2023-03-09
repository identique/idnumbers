from unittest import TestCase

from idnumbers.nationalid import ALB


class TestALBValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ALB.IdentityNumber.validate('I90308094A'))

    def test_error_case(self):
        self.assertFalse(ALB.IdentityNumber.validate('Z90308094Z'))

    def test_parse(self):
        result = ALB.IdentityNumber.parse('I90308094A')
        self.assertEqual(1989, result['yyyymmdd'].year)
        self.assertEqual(3, result['yyyymmdd'].month)
        self.assertEqual(8, result['yyyymmdd'].day)
        self.assertEqual('094', result['sn'])
        self.assertEqual('A', result['checksum'])
