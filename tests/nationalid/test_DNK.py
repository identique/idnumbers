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

    # Century rules: CPR-kontoret, "Personnummeret i CPR-systemet" (1 July 2008), table "Personnummerets opbygning",
    # https://cpr.dk/media/12066/personnummeret-i-cpr.pdf . The century depends on yy and the 7th digit.
    def test_parse_century(self):
        vectors = [
            ('0101451234', (1945, 1, 1)),
            ('2902004000', (2000, 2, 29)),
            ('0101585000', (1858, 1, 1)),
            ('0101995000', (1899, 1, 1)),
            ('0101379000', (1937, 1, 1)),
            ('0101374000', (1937, 1, 1)),
            ('0101005000', (2000, 1, 1)),
            ('0101009000', (2000, 1, 1)),
            ('0101990000', (1999, 1, 1)),
            ('0101000000', (1900, 1, 1)),
        ]
        for id_number, (year, month, day) in vectors:
            with self.subTest(id_number=id_number):
                result = DNK.PersonalIdentityNumber.parse(id_number)
                self.assertEqual(year, result['yyyymmdd'].year)
                self.assertEqual(month, result['yyyymmdd'].month)
                self.assertEqual(day, result['yyyymmdd'].day)

    def test_validate_century(self):
        valid = ['0101451234', '2902004000', '0101585000', '0101995000', '0101379000', '0101374000', '0101005000',
                 '0101009000', '0101990000', '0101000000', '0101801234']
        # 29 February 1900 does not exist (7th digit 0 means 19xx)
        invalid = ['2902000000']
        for cls in (DNK.PersonalIdentityNumber, DNK.NationalID, DNK.CPR):
            for id_number in valid:
                with self.subTest(cls=cls.__name__, id_number=id_number):
                    self.assertTrue(cls.validate(id_number))
            for id_number in invalid:
                with self.subTest(cls=cls.__name__, id_number=id_number):
                    self.assertFalse(cls.validate(id_number))

    def test_future_birth_date(self):
        # 7th digit 5 and yy 57 mean 1 January 2057, which stays in the future until then, so this test stays
        # correct until 2057.
        self.assertIsNone(DNK.PersonalIdentityNumber.parse('0101575000'))
        self.assertFalse(DNK.PersonalIdentityNumber.validate('0101575000'))

    def test_tin(self):
        self.assertTrue(DNK.TIN.individual.validate('0101801234'))
        self.assertTrue(DNK.TIN.entity.validate('88146328'))
        self.assertFalse(DNK.TIN.entity.validate('88146327'))
