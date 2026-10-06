from unittest import TestCase, main

from idnumbers.nationalid import ZWE


class TestNGAValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ZWE.NationalID.validate('75191961R00'))
        self.assertTrue(ZWE.NationalID.validate('751919620J86'))
        # real IDs reported in issue #277 (modulus 23 of the first 9 digits)
        self.assertTrue(ZWE.NationalID.validate('502001148W50'))
        self.assertTrue(ZWE.NationalID.validate('082095850T42'))

    def test_error_case(self):
        self.assertFalse(ZWE.NationalID.validate('75191962R00'))
        self.assertFalse(ZWE.NationalID.validate('00191962R58'))
        self.assertFalse(ZWE.NationalID.validate('40191962R75'))
        self.assertFalse(ZWE.NationalID.validate('40191962r75'))
        # the letter the old digit-sum rule gave
        self.assertFalse(ZWE.NationalID.validate('751919620S86'))
        self.assertFalse(ZWE.NationalID.validate('502001148X50'))
        self.assertFalse(ZWE.NationalID.validate('082095850P42'))

    def test_parse_11_digits(self):
        result = ZWE.NationalID.parse('75191961R00')
        self.assertEqual('75', result['register_office_code'])
        self.assertEqual('R', result['checksum'])
        self.assertEqual('00', result['district_code'])

    def test_parse_12_digits(self):
        result = ZWE.NationalID.parse('751910961X58')
        self.assertEqual('75', result['register_office_code'])
        self.assertEqual('X', result['checksum'])
        self.assertEqual('58', result['district_code'])

    def test_parse_leading_zero_office_code(self):
        # real ID from issue #277
        result = ZWE.NationalID.parse('082095850T42')
        self.assertEqual('08', result['register_office_code'])
        self.assertEqual('T', result['checksum'])
        self.assertEqual('42', result['district_code'])

    def test_checksum(self):
        self.assertTrue(ZWE.NationalID.checksum('751910961X58'))
        self.assertFalse(ZWE.NationalID.checksum('751910961R58'))


if __name__ == '__main__':
    main()
