from datetime import date
from unittest import TestCase
from unittest.mock import patch

from idnumbers.nationalid import ALB
from idnumbers.nationalid.constant import Gender


class TestALBValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ALB.NationalID.validate('I90308094A'))

    def test_error_case(self):
        self.assertFalse(ALB.NationalID.validate('Z90308094Z'))

    def test_parse(self):
        result = ALB.NationalID.parse('I90308094A')
        self.assertEqual(1989, result['yyyymmdd'].year)
        self.assertEqual(3, result['yyyymmdd'].month)
        self.assertEqual(8, result['yyyymmdd'].day)
        self.assertEqual('094', result['sn'])
        self.assertEqual('A', result['checksum'])

    def test_alias(self):
        self.assertIsNone(ALB.IdentityNumber.METADATA.alias_of)
        self.assertEqual(ALB.IdentityNumber, ALB.NationalID.METADATA.alias_of)

    def setUp(self):
        clock = patch('idnumbers.nationalid.alb.identity_number.date', wraps=date)
        self.mock_date = clock.start()
        self.addCleanup(clock.stop)
        self.mock_date.today.return_value = date(2026, 10, 7)

    def test_metadata_names(self):
        names = ['Albania Identity Number', 'Numri i Identitetit', 'NID',
                 'Numri i Identitetit të Shtetasit', 'NISH', 'NIPT']
        self.assertEqual(names, ALB.IdentityNumber.METADATA.names)
        self.assertEqual(names, ALB.NationalID.METADATA.names)
        self.assertFalse(ALB.IdentityNumber.METADATA.checksum)

    def test_birth_date_boundary(self):
        # Synthetic format/date vectors; not claimed issued or checksum-validated.
        for gender, month in ((Gender.MALE, 10), (Gender.FEMALE, 60)):
            for day, valid in ((6, True), (7, True), (8, False)):
                for separator in ('', ' ', '-'):
                    number = f'M6{month:02d}{day:02d}001{separator}A'
                    with self.subTest(number=number):
                        self.assertEqual(valid, ALB.NationalID.validate(number))
                        result = ALB.NationalID.parse(number)
                        if valid:
                            self.assertEqual({'yyyymmdd': date(2026, 10, day), 'gender': gender,
                                              'sn': '001', 'checksum': 'A'}, result)
                            self.assertIsInstance(result['yyyymmdd'], date)
                            self.assertIsInstance(result['gender'], Gender)
                            self.assertIsInstance(result['sn'], str)
                            self.assertIsInstance(result['checksum'], str)
                        else:
                            self.assertIsNone(result)

    def test_future_birth_dates(self):
        for number in ('M61031001A', 'M61101001A', 'M66031001A', 'M66101001A',
                       'N00101001A', 'N05101001A', 'T50101001A', 'T55101001A'):
            with self.subTest(number=number):
                self.assertFalse(ALB.NationalID.validate(number))
                self.assertIsNone(ALB.NationalID.parse(number))

    def test_new_decade_is_accepted_when_today_advances(self):
        self.mock_date.today.return_value = date(2030, 1, 1)
        for number in ('N00101001A', 'N05101001A'):
            with self.subTest(number=number):
                self.assertTrue(ALB.NationalID.validate(number))
                self.assertEqual(date(2030, 1, 1), ALB.NationalID.parse(number)['yyyymmdd'])
        for number in ('N00102001A', 'N05102001A'):
            with self.subTest(number=number):
                self.assertFalse(ALB.NationalID.validate(number))
                self.assertIsNone(ALB.NationalID.parse(number))

    def test_existing_year_decoding(self):
        prefixes = '0123456789ABCDEFGHIJKLMNOPQRST'
        self.assertEqual(prefixes, ALB.IdentityNumber.BASE_YEAR_MAP)
        for index, prefix in enumerate(prefixes):
            for digit in range(10):
                yy = f'{prefix}{digit}'
                self.assertEqual(1800 + index * 10 + digit, ALB.IdentityNumber.get_year(yy))
        for yy, year in (('00', 1800), ('90', 1890), ('A0', 1900), ('J0', 1990), ('K0', 2000)):
            for month in ('01', '51'):
                number = f'{yy}{month}01001A'
                with self.subTest(number=number):
                    self.assertTrue(ALB.NationalID.validate(number))
                    self.assertEqual(date(year, 1, 1), ALB.NationalID.parse(number)['yyyymmdd'])

    def test_calendar_dates(self):
        for number in ('K00229001A', 'K05229001A'):
            with self.subTest(number=number):
                self.assertTrue(ALB.NationalID.validate(number))
                self.assertEqual(date(2000, 2, 29), ALB.NationalID.parse(number)['yyyymmdd'])
        for number in ('A00229001A', 'A05229001A', 'M60001001A', 'M65001001A',
                       'M61301001A', 'M66301001A', 'M60230001A', 'M65230001A',
                       'M60100001A', 'M65100001A', 'M60132001A', 'M65132001A'):
            with self.subTest(number=number):
                self.assertFalse(ALB.NationalID.validate(number))
                self.assertIsNone(ALB.NationalID.parse(number))

    def test_malformed_input(self):
        for number in (None, 123, b'I90308094A', [], {}, '', 'I90308094A\n',
                       'I９0308094A', 'I9٠308094A', ' I90308094A', 'I90308094A ',
                       'I90308094--A', 'I90308094_A', 'I90308094a', 'I90308094X'):
            with self.subTest(number=number):
                self.assertFalse(ALB.NationalID.validate(number))
                self.assertIsNone(ALB.NationalID.parse(number))
