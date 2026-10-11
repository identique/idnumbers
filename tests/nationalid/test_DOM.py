from unittest import TestCase

import idnumbers
from idnumbers.nationalid import DOM


class TestDOMValidation(TestCase):
    def test_country_metadata(self):
        self.assertEqual(DOM.NationalID.METADATA.iso3166_alpha2, 'DO')
        self.assertEqual(DOM.NationalID.METADATA.country_name, 'Dominican Republic')
        self.assertTrue(DOM.NationalID.METADATA.checksum)
        self.assertTrue(DOM.NationalID.validate(DOM.NationalID.METADATA.example))

    def test_normal_case(self):
        for id_number in (
            '40200000012',  # Node port test vector
            '00100000017',  # Node port test vector
            '03112345677',  # Node port test vector
            '00113918205',  # python-stdnum doctest example
            '22400022111',  # python-stdnum doctest example
            '402-0000001-2',
            '402-1234567-8',  # synthetic
            '4021234567-8',  # one optional hyphen
            '402-12345678',  # one optional hyphen
        ):
            with self.subTest(id_number=id_number):
                self.assertTrue(DOM.NationalID.validate(id_number))

    def test_error_case(self):
        for id_number in (
            '40200000013',  # wrong check digit
            '00100000018',  # wrong check digit
            '03112345678',  # wrong check digit
            '00113918204',  # wrong check digit
            '402-1234567-0',  # wrong check digit
            '4020000001',  # 10 digits
            '402000000122',  # 12 digits
            # in python-stdnum's list of issued cédulas that fail Luhn; deliberately not accepted, see issue #517
            '00000021249',
            '000-0002124-9',
            '402 0000001 2',  # spaces
            '402--0000001-2',
            '4020000001-2-',
            '402-0000001-2\n',
            '40200000012\n',  # trailing newline
            ' 40200000012',  # leading space
            '４０２００００００１２',  # full-width digits
            '0011391820A',
            '',
        ):
            with self.subTest(id_number=id_number):
                self.assertFalse(DOM.NationalID.validate(id_number))
                self.assertIsNone(DOM.NationalID.parse(id_number))

    def test_non_string_input(self):
        for value in (None, 40200000012):
            with self.subTest(value=value):
                self.assertFalse(DOM.NationalID.validate(value))  # type: ignore[arg-type]
                self.assertIsNone(DOM.NationalID.parse(value))  # type: ignore[arg-type]
                self.assertIsNone(DOM.NationalID.checksum(value))  # type: ignore[arg-type]

    def test_parse(self):
        self.assertEqual({'series': '402', 'sequence': '0000001', 'checksum': 2},
                         DOM.NationalID.parse('402-0000001-2'))
        self.assertEqual(DOM.NationalID.parse('402-0000001-2'), DOM.NationalID.parse('40200000012'))
        self.assertEqual({'series': '001', 'sequence': '1391820', 'checksum': 5},
                         DOM.NationalID.parse('00113918205'))

    def test_checksum(self):
        self.assertEqual(2, DOM.NationalID.checksum('40200000012'))
        self.assertEqual(2, DOM.NationalID.checksum('402-0000001-2'))
        # the computed digit does not depend on the number's own last digit
        self.assertEqual(2, DOM.NationalID.checksum('40200000013'))
        self.assertEqual(5, DOM.NationalID.checksum('00113918204'))
        self.assertEqual(8, DOM.NationalID.checksum('402-1234567-0'))
        for id_number in ('', '4020000001', '402 0000001 2', '40200000012\n', '0011391820A'):
            with self.subTest(id_number=id_number):
                self.assertIsNone(DOM.NationalID.checksum(id_number))

    def test_every_check_digit_is_unique(self):
        # for a fixed prefix exactly one of the ten possible last digits is valid
        for prefix in ('4020000001', '0011391820', '4021234567'):
            valid = [digit for digit in range(10) if DOM.NationalID.validate('%s%d' % (prefix, digit))]
            self.assertEqual([DOM.NationalID.checksum(prefix + '0')], valid)

    def test_unified_api(self):
        self.assertTrue(idnumbers.validate('DOM', '402-0000001-2'))
        self.assertTrue(idnumbers.validate('DO', '40200000012'))
        self.assertFalse(idnumbers.validate('DO', '40200000013'))
        self.assertFalse(idnumbers.validate('DO', '00000021249'))
        info = idnumbers.parse_id_info('DO', '402-0000001-2')
        assert info.ok
        self.assertEqual('402', info.info['series'])
        self.assertEqual(2, info.info['checksum'])
