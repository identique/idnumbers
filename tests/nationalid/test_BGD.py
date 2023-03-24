from unittest import TestCase

from idnumbers.nationalid import BGD


class TestBGDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(BGD.OldNationalID.validate('1592824588424'))
        self.assertTrue(BGD.OldNationalID.validate('2610413965404'))
        self.assertTrue(BGD.NationalID.validate('19841592824588424'))
        self.assertTrue(BGD.NationalID.validate('19892610413965404'))

    def test_error_case(self):
        self.assertFalse(BGD.OldNationalID.validate('159282458842'))
        self.assertFalse(BGD.OldNationalID.validate('1572824588424'))
        self.assertFalse(BGD.NationalID.validate('1984159282458844'))

    def test_parse(self):
        old_result = BGD.OldNationalID.parse('1592824588424')
        self.assertEqual('15', old_result['distinct'])
        self.assertEqual(BGD.ResidentialType.CITY_CORPORATION, old_result['residential_type'])
        self.assertEqual('28', old_result['policy_station_no'])
        self.assertEqual('24', old_result['union_code'])
        self.assertEqual('588424', old_result['sn'])

        result = BGD.NationalID.parse('19892610413965404')
        self.assertEqual(1989, result['yyyy'])
        self.assertEqual('26', result['distinct'])
        self.assertEqual(BGD.ResidentialType.RURAL, result['residential_type'])
        self.assertEqual('04', result['policy_station_no'])
        self.assertEqual('13', result['union_code'])
        self.assertEqual('965404', result['sn'])
