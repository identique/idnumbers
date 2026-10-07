from datetime import date
from unittest import TestCase

from idnumbers.nationalid import MNE
from idnumbers.nationalid.constant import Citizenship


class TestMNEDocumentation(TestCase):
    def test_country_and_location_documentation(self):
        cls = MNE.UniqueMasterCitizenNumber
        self.assertIn('Montenegro', cls.__doc__)
        self.assertNotIn('Serbia', cls.__doc__)
        self.assertIn('Montenegro', cls.check_location.__doc__)
        self.assertIn('20 < location < 30', cls.check_location.__doc__)
        self.assertIn('(RESIDENT, location)', cls.check_location.__doc__)
        self.assertIn('None for an invalid location', cls.check_location.__doc__)

    def test_existing_location_policy(self):
        cls = MNE.UniqueMasterCitizenNumber
        for location in ('21', '29'):
            self.assertEqual((Citizenship.CITIZEN, location), cls.check_location(location))
        self.assertEqual((Citizenship.RESIDENT, '10'), cls.check_location('10'))
        self.assertIsNone(cls.check_location('20'))
        self.assertIsNone(cls.check_location('99'))

    def test_existing_validation_and_parse(self):
        # Synthetic JMBG: 1990-01-01, local region, serial 001; existing weighted checksum gives 3.
        cls = MNE.UniqueMasterCitizenNumber
        value = '0101990210013'
        self.assertTrue(cls.validate(value))
        self.assertTrue(cls.checksum(value))
        result = cls.parse(value)
        self.assertEqual(date(1990, 1, 1), result['yyyymmdd'])
        self.assertEqual('21', result['location'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])
        self.assertEqual('001', result['sn'])
        self.assertEqual(3, result['checksum'])
        self.assertFalse(cls.validate(value[:-1] + '4'))
        self.assertIsNone(cls.parse(value[:-1] + '4'))
