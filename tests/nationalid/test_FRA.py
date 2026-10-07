from unittest import TestCase, main

from idnumbers.nationalid.constant import Gender
from idnumbers.nationalid import FRA


class TestFRAValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(FRA.NationalID.validate('255081416802538'))
        self.assertTrue(FRA.NationalID.validate('283209921625930'))
        self.assertTrue(FRA.NationalID.validate('255082a16802597'))

    def test_error_case(self):
        self.assertFalse(FRA.NationalID.validate('180126955222381'))
        self.assertFalse(FRA.NationalID.validate('255082e16802597'))

    def test_parse(self):
        result = FRA.NationalID.parse('255082a16802597')
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('55', result['yy'])
        self.assertEqual('08', result['mm'])
        self.assertEqual('97', result['checksum'])

    def test_birth_department_96(self):
        # 91-96 were Algeria, Morocco and Tunisia before 1964; key = 97 - first 13 digits mod 97
        self.assertTrue(FRA.NationalID.validate('145089612304582'))
        self.assertTrue(FRA.NationalID.validate('145089512304512'))
        result = FRA.NationalID.parse('145089612304582')
        self.assertEqual({'department': '96', 'city': '123', 'country': ''}, result['birth_department'])

    def test_birth_department_96_wrong_key(self):
        self.assertFalse(FRA.NationalID.validate('145089612304583'))

    def test_birth_department_00(self):
        # correct key (55), but there is no department 00
        self.assertFalse(FRA.NationalID.validate('145080012304555'))
        self.assertIsNone(FRA.NationalID.parse('145080012304555'))

    def test_parse_gender(self):
        # 1 is male, 7 is a temporary number for a man (ameli: "commence par un 7 si vous etes un homme")
        self.assertEqual(Gender.MALE, FRA.NationalID.parse('145089512304512')['gender'])
        self.assertEqual(Gender.MALE, FRA.NationalID.parse('785087512304538')['gender'])
        # 2 is female, 8 is a temporary number for a woman
        self.assertEqual(Gender.FEMALE, FRA.NationalID.parse('285087512304594')['gender'])
        self.assertEqual(Gender.FEMALE, FRA.NationalID.parse('885087512304585')['gender'])

    def test_parse_gender_code_3(self):
        # pins the current behaviour: no source says which sex 3 and 4 stand for, see
        # https://github.com/identique/idnumbers/issues/429
        self.assertTrue(FRA.NationalID.validate('385087512304544'))
        self.assertEqual(Gender.FEMALE, FRA.NationalID.parse('385087512304544')['gender'])


if __name__ == '__main__':
    main()
