from unittest import TestCase

import idnumbers
from idnumbers.nationalid import CRI
from idnumbers.nationalid.cri.national_id import PROVINCE_NAMES


class TestCRIValidation(TestCase):
    def test_country_metadata(self):
        self.assertEqual(CRI.NationalID.METADATA.iso3166_alpha2, 'CR')
        self.assertEqual(CRI.NationalID.METADATA.country_name, 'Costa Rica')
        self.assertFalse(CRI.NationalID.METADATA.checksum)
        self.assertTrue(CRI.NationalID.validate(CRI.NationalID.METADATA.example))

    def test_normal_case(self):
        for id_number in (
            '1-0913-0259',  # Hacienda help-page example
            '109130259',
            '3-0455-0175',  # python-stdnum documentation example
            '701610395',  # python-stdnum documentation example
            '8-0123-0456',  # synthetic: naturalized citizen
            '9-0123-0456',  # synthetic: special birth register
            '1-0234-0567',  # synthetic
        ):
            with self.subTest(id_number=id_number):
                self.assertTrue(CRI.NationalID.validate(id_number))

    def test_error_case(self):
        for id_number in (
            '009130259',  # province 0
            '0-0913-0259',  # province 0
            '0109130259',  # python-stdnum 10-digit Hacienda form
            '01-0913-0259',  # python-stdnum 10-digit Hacienda form
            '1091302599',  # 10 digits
            '3101123456',  # cédula jurídica
            '155812345678',  # 12-digit DIMEX
            '12345678901',  # 11 digits
            '10913025',  # 8 digits
            '1-913-259',  # unpadded
            '1 0913 0259',  # unsupported separator
            '1/0913/0259',  # unsupported separator
            '1--0913-0259',
            '109130259\n',  # trailing newline
            ' 109130259',  # leading space
            '１０９１３０２５９',  # full-width digits
            '',
        ):
            with self.subTest(id_number=id_number):
                self.assertFalse(CRI.NationalID.validate(id_number))
                self.assertIsNone(CRI.NationalID.parse(id_number))

    def test_non_string_input(self):
        for value in (None, 109130259):
            with self.subTest(value=value):
                self.assertFalse(CRI.NationalID.validate(value))  # type: ignore[arg-type]
                self.assertIsNone(CRI.NationalID.parse(value))  # type: ignore[arg-type]

    def test_parse(self):
        self.assertEqual(
            {'province': 1, 'province_name': 'San José', 'tomo': '0913', 'asiento': '0259'},
            CRI.NationalID.parse('1-0913-0259'))
        self.assertEqual(CRI.NationalID.parse('1-0913-0259'), CRI.NationalID.parse('109130259'))
        naturalized = CRI.NationalID.parse('8-0123-0456')
        assert naturalized is not None
        self.assertEqual(8, naturalized['province'])
        self.assertEqual('Naturalized', naturalized['province_name'])
        special = CRI.NationalID.parse('9-0123-0456')
        assert special is not None
        self.assertEqual('Partida Especial de Nacimientos', special['province_name'])

    def test_every_province_has_a_name(self):
        self.assertEqual(set(range(1, 10)), set(PROVINCE_NAMES))
        for province in range(1, 10):
            with self.subTest(province=province):
                result = CRI.NationalID.parse('%d-0123-0456' % province)
                assert result is not None
                self.assertEqual(PROVINCE_NAMES[province], result['province_name'])

    def test_unified_api(self):
        self.assertTrue(idnumbers.validate('CRI', '1-0913-0259'))
        self.assertTrue(idnumbers.validate('CR', '109130259'))
        self.assertFalse(idnumbers.validate('CR', '0109130259'))
        info = idnumbers.parse_id_info('CR', '1-0913-0259')
        assert info.ok
        self.assertEqual('San José', info.info['province_name'])
