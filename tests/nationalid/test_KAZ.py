from unittest import TestCase, main

from idnumbers.nationalid import KAZ


class TestKAZValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(KAZ.IndividualIDNumber.validate('901123300258'))
        self.assertTrue(KAZ.BusinessIDNumber.validate('990940003030'))

    def test_error_case(self):
        self.assertFalse(KAZ.IndividualIDNumber.validate('901123300255'))
        self.assertFalse(KAZ.BusinessIDNumber.validate('990940003031'))

    def test_parse(self):
        result = KAZ.IndividualIDNumber.parse('901123300258')
        self.assertEqual(1990, result['yyyymmdd'].year)
        self.assertEqual(11, result['yyyymmdd'].month)
        self.assertEqual(23, result['yyyymmdd'].day)
        self.assertEqual('0025', result['sn'])
        self.assertEqual(8, result['checksum'])

        result = KAZ.BusinessIDNumber.parse('990940003030')
        self.assertEqual(99, result['yy'])
        self.assertEqual(9, result['mm'])
        self.assertEqual(KAZ.EntityType.ResidentEntity, result['entity_type'])
        self.assertEqual(KAZ.EntityDivision.HeadUnit, result['entity_division'])
        self.assertEqual('00303', result['sn'])
        self.assertEqual(0, result['checksum'])
