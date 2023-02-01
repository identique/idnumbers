from unittest import TestCase, main

from idnumbers.nationalid import SVN
from idnumbers.nationalid.constant import Gender


class TestSVNValidation(TestCase):
    """
    It tests for SVN, SRB, MKD, MNE, BIH
    """
    def test_normal_case(self):
        self.assertTrue(SVN.UniqueMasterCitizenNumber.validate('0101006500006'))
        self.assertTrue(SVN.UniqueMasterCitizenNumber.validate('0101001735005'))
        self.assertTrue(SVN.UniqueMasterCitizenNumber.validate('1905983710332'))
        self.assertTrue(SVN.UniqueMasterCitizenNumber.validate('2908004303910'))

    def test_error_case(self):
        self.assertFalse(SVN.UniqueMasterCitizenNumber.validate('0101006500007'))

    def test_parse(self):
        result = SVN.UniqueMasterCitizenNumber.parse('0101006500006')
        self.assertEqual(2006, result['yyyymmdd'].year)
        self.assertEqual(1, result['yyyymmdd'].month)
        self.assertEqual(1, result['yyyymmdd'].day)
        self.assertEqual('50', result['location'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('000', result['sn'])
        self.assertEqual(6, result['checksum'])


if __name__ == '__main__':
    main()
