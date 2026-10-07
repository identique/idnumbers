from datetime import date
from unittest import TestCase

from idnumbers.nationalid import BIH
from idnumbers.nationalid.constant import Citizenship


class TestBIHDocumentation(TestCase):
    def test_country_and_location_documentation(self):
        cls = BIH.UniqueMasterCitizenNumber
        self.assertIn('Bosnia and Herzegovina', cls.__doc__)
        self.assertNotIn('Serbia', cls.__doc__)
        self.assertIn('Bosnia and Herzegovina', cls.check_location.__doc__)
        self.assertIn('10 <= location < 20', cls.check_location.__doc__)
        self.assertIn('(RESIDENT, location)', cls.check_location.__doc__)
        self.assertIn('None for an invalid location', cls.check_location.__doc__)

    def test_existing_location_policy(self):
        cls = BIH.UniqueMasterCitizenNumber
        for location in ('10', '19'):
            self.assertEqual((Citizenship.CITIZEN, location), cls.check_location(location))
        self.assertEqual((Citizenship.RESIDENT, '21'), cls.check_location('21'))
        self.assertIsNone(cls.check_location('20'))
        self.assertIsNone(cls.check_location('99'))

    def test_existing_validation_and_parse(self):
        # Synthetic JMBG: 1990-01-01, local region, serial 001; existing weighted checksum gives 3.
        cls = BIH.UniqueMasterCitizenNumber
        value = '0101990100013'
        self.assertTrue(cls.validate(value))
        self.assertTrue(cls.checksum(value))
        result = cls.parse(value)
        self.assertEqual(date(1990, 1, 1), result['yyyymmdd'])
        self.assertEqual('10', result['location'])
        self.assertEqual(Citizenship.CITIZEN, result['citizenship'])
        self.assertEqual('001', result['sn'])
        self.assertEqual(3, result['checksum'])
        self.assertFalse(cls.validate(value[:-1] + '4'))
        self.assertIsNone(cls.parse(value[:-1] + '4'))
