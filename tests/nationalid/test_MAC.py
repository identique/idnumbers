from unittest import TestCase

from idnumbers.nationalid import MAC


class TestMACValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(MAC.NationalID.validate('5215299(8)'))
        self.assertTrue(MAC.NationalID.validate('12281507'))
        self.assertTrue(MAC.NationalID.validate('82152998'))
        self.assertTrue(MAC.NationalID.validate('02281507'))

    def test_error_case(self):
        self.assertFalse(MAC.NationalID.validate('22281507'))

    def test_parse(self):
        result = MAC.NationalID.parse('12281507')
        self.assertEqual(MAC.DocType.FIRST_GEN, result['doc_type'])
        self.assertEqual('2281507', result['sn'])

        result = MAC.NationalID.parse('02281507')
        self.assertEqual(MAC.DocType.CI, result['doc_type'])
        self.assertEqual('2281507', result['sn'])
