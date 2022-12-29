from unittest import TestCase, main

from idnumbers.nationalid import KOR
from idnumbers.nationalid.constant import Gender, Citizenship


class TestKORValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(KOR.NationalID.validate('820701-2409184'))
        self.assertTrue(KOR.NationalID.validate('850408-5761193'))
        self.assertTrue(KOR.NationalID.validate('860121-4500147'))
        self.assertTrue(KOR.OldNationalID.validate('510724-1057122'))
        self.assertTrue(KOR.OldNationalID.validate('690212-1148921'))
        self.assertTrue(KOR.OldNationalID.validate('731228-2686181'))
        self.assertTrue(KOR.ARC.validate('850526-6260197'))
        self.assertTrue(KOR.ARC.validate('840609-5260291'))

    def test_error_case(self):
        self.assertFalse(KOR.OldNationalID.validate('820701-2409184'))
        self.assertFalse(KOR.NationalID.validate('8207012409184'))

    def test_parse(self):
        result = KOR.NationalID.parse('820701-2409184')
        self.assertEqual(1982, result['yyyymmdd'].year)
        self.assertEqual(7, result['yyyymmdd'].month)
        self.assertEqual(1, result['yyyymmdd'].day)
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])
        self.assertEqual('409184', result['sn'])
        result = KOR.ARC.parse('850526-6260197')
        self.assertEqual(1985, result['yyyymmdd'].year)
        self.assertEqual(5, result['yyyymmdd'].month)
        self.assertEqual(26, result['yyyymmdd'].day)
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual(Citizenship.FOREIGNER, result['citizenship'])
        self.assertEqual('260197', result['sn'])

        result = KOR.OldNationalID.parse('510724-1057122')
        self.assertEqual(1951, result['yyyymmdd'].year)
        self.assertEqual(7, result['yyyymmdd'].month)
        self.assertEqual(24, result['yyyymmdd'].day)
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])
        self.assertEqual('0571', result['location'])
        self.assertEqual('2', result['sn'])
        self.assertEqual(2, result['checksum'])


if __name__ == '__main__':
    main()
