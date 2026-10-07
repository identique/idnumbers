from unittest import TestCase

from idnumbers.nationalid import MAC


class TestMACValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(MAC.NationalID.validate('5215299(8)'))
        self.assertTrue(MAC.NationalID.validate('12281507'))
        self.assertTrue(MAC.NationalID.validate('82152998'))
        self.assertTrue(MAC.NationalID.validate('02281507'))

    def test_error_case(self):
        self.assertFalse(MAC.NationalID.validate('22281507'))

    def test_parse(self):
        result = MAC.NationalID.parse('12281507')
        self.assertEqual(MAC.DocType.FIRST_GEN, result['doc_type'])
        self.assertEqual('2281507', result['sn'])

        result = MAC.NationalID.parse('02281507')
        self.assertEqual(MAC.DocType.CI, result['doc_type'])
        self.assertEqual('2281507', result['sn'])

    def test_supported_layouts_and_parse_payload(self):
        # Synthetic format vectors, not verified issued IDs or checksum vectors.
        types = {'0': MAC.DocType.CI, '1': MAC.DocType.FIRST_GEN,
                 '5': MAC.DocType.MCA, '7': MAC.DocType.MPSP, '8': MAC.DocType.ENTITY}
        for name in ('NationalID', 'BIRP', 'BIRNP', 'ARC'):
            cls = getattr(MAC, name)
            for prefix, doc_type in types.items():
                for extra in '0123456789':
                    body = prefix + '215432'
                    expected = {'doc_type': doc_type, 'sn': '215432' + extra}
                    for value in (body + extra, body + '(' + extra + ')'):
                        with self.subTest(alias=name, value=value):
                            self.assertTrue(cls.validate(value))
                            self.assertEqual(expected, cls.parse(value))

    def test_malformed_layouts_and_inputs(self):
        invalid = (
            '5215432(8', '52154328)', '5215432(', '5215432)',
            '5215432()', '5215432((8)', '5215432(8))', '5215432((8))',
            '(52154328)', '521(5432)8', '521543(28)', '5215432)(8',
            '5215432（8）', '5215432（8)', '5215432(8）',
            '5215432', '521543288', '5215432(88)', '5215432 8',
            '52154328\n', '5215432(8)\n', '\n52154328',
            '５２１５４３２８', '٥٢١٥٤٣٢٨', '5２１５４３２(８)',
            '', None, 52154328, b'52154328', [], {}, True,
        )
        for name in ('NationalID', 'BIRP', 'BIRNP', 'ARC'):
            cls = getattr(MAC, name)
            for value in invalid:
                with self.subTest(alias=name, value=value):
                    self.assertFalse(cls.validate(value))
                    self.assertIsNone(cls.parse(value))
            for prefix in '23469':
                for value in (prefix + '2154328', prefix + '215432(8)'):
                    with self.subTest(alias=name, value=value):
                        self.assertFalse(cls.validate(value))
                        self.assertIsNone(cls.parse(value))

    def test_metadata_and_capture_groups(self):
        # Length metadata counts significant digits, excluding paired parentheses.
        for name in ('NationalID', 'BIRP', 'BIRNP', 'ARC'):
            metadata = getattr(MAC, name).METADATA
            with self.subTest(alias=name):
                self.assertEqual((8, 8), (metadata.min_length, metadata.max_length))
                self.assertFalse(metadata.checksum)
                self.assertEqual(3, metadata.regexp.groups)
                self.assertEqual({'doc_type': 1, 'sn': 2, 'extra': 3},
                                 metadata.regexp.groupindex)
                for value in ('52154328', '5215432(8)'):
                    match = metadata.regexp.fullmatch(value)
                    self.assertEqual(('5', '215432', '8'), match.groups())
                    self.assertEqual({'doc_type': '5', 'sn': '215432', 'extra': '8'},
                                     match.groupdict())
