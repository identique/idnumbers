from unittest import TestCase

from idnumbers.nationalid import DNK


class TestDNKValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(DNK.PersonalIdentityNumber.validate('061085-1178'))

    def test_error_case(self):
        self.assertFalse(DNK.PersonalIdentityNumber.validate('061085-178'))

    def test_parse(self):
        result = DNK.PersonalIdentityNumber.parse('061085-1178')
        self.assertEqual(1985, result['yyyymmdd'].year)
        self.assertEqual(10, result['yyyymmdd'].month)
        self.assertEqual(6, result['yyyymmdd'].day)
        self.assertEqual('1178', result['sn'])

    def test_tin(self):
        self.assertTrue(DNK.TIN.individual.validate('0101801234'))
        self.assertTrue(DNK.TIN.entity.validate('88146328'))
        self.assertFalse(DNK.TIN.entity.validate('88146327'))
