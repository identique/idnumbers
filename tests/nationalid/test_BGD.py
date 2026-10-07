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
        self.assertEqual('1989', result['yyyy'])
        self.assertIsInstance(result['yyyy'], str)
        self.assertEqual('26', result['distinct'])
        self.assertEqual(BGD.ResidentialType.RURAL, result['residential_type'])
        self.assertEqual('04', result['policy_station_no'])
        self.assertEqual('13', result['union_code'])
        self.assertEqual('965404', result['sn'])

    def test_year_string_preserves_leading_zeros(self):
        # Synthetic vectors exercise representation, not a new birth-year policy.
        old_number = '1592824588424'
        expected_old_result = {
            'distinct': '15',
            'residential_type': BGD.ResidentialType.CITY_CORPORATION,
            'policy_station_no': '28',
            'union_code': '24',
            'sn': '588424'
        }
        self.assertEqual(expected_old_result, BGD.OldNationalID.parse(old_number))
        for year in ('0000', '0001', '0099', '0999', '1984'):
            with self.subTest(year=year):
                number = year + old_number
                self.assertTrue(BGD.NationalID.validate(number))
                result = BGD.NationalID.parse(number)
                self.assertIsNotNone(result)
                self.assertIsInstance(result['yyyy'], str)
                self.assertEqual(year, result['yyyy'])
                self.assertEqual(4, len(result['yyyy']))
                self.assertEqual({**expected_old_result, 'yyyy': year}, result)

    def test_metadata_lengths(self):
        for id_class, number, length in (
                (BGD.NationalID, '19841592824588424', 17),
                (BGD.OldNationalID, '1592824588424', 13)):
            with self.subTest(id_class=id_class):
                self.assertEqual(length, id_class.METADATA.min_length)
                self.assertEqual(length, id_class.METADATA.max_length)
                self.assertEqual(length, len(number))
                self.assertTrue(id_class.validate(number))

    def test_invalid_inputs(self):
        for id_class, number in (
                (BGD.NationalID, '19841592824588424'),
                (BGD.OldNationalID, '1592824588424')):
            invalid_inputs = (
                None, False, 0, 19841592824588424, [], {}, number.encode(), '',
                number[:-1], number + '0', 'x' + number, number + 'x',
                ' ' + number, number + ' ', number + '\n',
                ''.join(chr(ord(char) + 0xFEE0) for char in number),
                ''.join(chr(0x0660 + int(char)) for char in number)
            )
            for value in invalid_inputs:
                with self.subTest(id_class=id_class, value=value):
                    self.assertFalse(id_class.validate(value))
                    self.assertIsNone(id_class.parse(value))

    def test_invalid_residential_type(self):
        for id_class, number in (
                (BGD.NationalID, '19841572824588424'),
                (BGD.OldNationalID, '1572824588424')):
            with self.subTest(id_class=id_class):
                self.assertFalse(id_class.validate(number))
                self.assertIsNone(id_class.parse(number))
