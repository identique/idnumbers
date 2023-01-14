from unittest import TestCase, main

from idnumbers.nationalid import POL
from idnumbers.nationalid.constant import Gender


class TestPOLValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(POL.PESEL.validate('81010200141'))
        self.assertTrue(POL.PESEL.validate('02070803628'))
        self.assertTrue(POL.PESEL.validate('83020410655'))

    def test_error_case(self):
        self.assertFalse(POL.PESEL.validate('02070803629'))

    def test_parse(self):
        result = POL.PESEL.parse('02070803628')
        self.assertEqual(1902, result['yyyymmdd'].year)
        self.assertEqual(7, result['yyyymmdd'].month)
        self.assertEqual(8, result['yyyymmdd'].day)
        self.assertEqual('0362', result['sn'])
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual(8, result['checksum'])


if __name__ == '__main__':
    main()
