from datetime import date
from unittest import TestCase, main

from idnumbers.nationalid import MEX
from idnumbers.nationalid.constant import Gender


# RENAPO, Instructivo Normativo (March 2006), Annex 2, printed page 59.
# Original inconvenient words, transcribed independently from the primary catalogue.
# https://ordenjuridico.gob.mx/Federal/PE/APF/APC/SEGOB/Instructivos/InstructivoNormativo.pdf
_INCONVENIENT_WORDS = (
    'BACA BAKA BUEI BUEY CACA CACO CAGA CAGO CAKA CAKO COGE COGI COJA COJE COJI COJO '
    'COLA CULO FALO FETO GETA GUEI GUEY JETA JOTO KACA KACO KAGA KAGO KAKA KAKO KOGE '
    'KOGI KOJA KOJE KOJI KOJO KOLA KULO LILO LOCA LOCO LOKA LOKO MAME MAMO MEAR MEAS '
    'MEON MIAR MION MOCO MOKO MULA MULO NACA NACO PEDA PEDO PENE PIPI PITO POPO PUTA '
    'PUTO QULO RATA ROBA ROBE ROBO RUIN SENO TETA VACA VAGA VAGO VAKA VUEI VUEY WUEI WUEY'
).split()


def _synthetic_curp(prefix, birth='560427', gender='H', location='VZ', serial='0'):
    # Algorithm probes only: these generated values are not claims of issued IDs.
    body = prefix + birth + gender + location + 'RRL' + serial
    alphabet = '0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'
    weighted_total = sum(alphabet.index(char) * weight for char, weight in zip(body, range(18, 1, -1)))
    return body + str((-weighted_total) % 10)


def _expected_parse(value):
    return {
        'name_initial_chars': value[:4],
        'name_consonants': 'RRL',
        'yyyymmdd': date(1956 if value[16] == '0' else 2056, 4, 27),
        'gender': {'H': Gender.MALE, 'M': Gender.FEMALE, 'X': Gender.NON_BINARY}[value[10]],
        'location': value[11:13],
        'sn': value[16],
        'checksum': int(value[17]),
    }


class TestMEXValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(MEX.NationalID.validate('HEGG560427MVZRRL04'))
        self.assertTrue(MEX.NationalID.validate('AUAM630703HGTGRR02'))
        self.assertTrue(MEX.NationalID.validate('HORA500201MNELSR04'))
        self.assertTrue(MEX.NationalID.validate('CAMP800404HNEHDD03'))
        self.assertTrue(MEX.NationalID.validate('DIXM870113HNEFXS06'))
        self.assertTrue(MEX.NationalID.validate('MACD880521HNERVN09'))
        self.assertTrue(MEX.NationalID.validate('DIXB881003HNELXB01'))
        self.assertTrue(MEX.NationalID.validate('SOMD911221HNEBJN03'))

    def test_error_case(self):
        self.assertFalse(MEX.NationalID.validate('HEGG560427MVZRRL05'))
        self.assertFalse(MEX.NationalID.validate('AUAM630703KGTGRR02'))
        self.assertFalse(MEX.NationalID.validate('HEGGGG0427MVZRRL05'))
        self.assertFalse(MEX.NationalID.validate('HEGG560427MXXRRL05'))

    def test_parse(self):
        result = MEX.NationalID.parse('HEGG560427MVZRRL04')
        self.assertEqual('HEGG', result['name_initial_chars'])
        self.assertEqual(1956, result['yyyymmdd'].year)
        self.assertEqual(4, result['yyyymmdd'].month)
        self.assertEqual(27, result['yyyymmdd'].day)
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('VZ', result['location'])
        self.assertEqual('RRL', result['name_consonants'])
        self.assertEqual('0', result['sn'])
        self.assertEqual(4, result['checksum'])

    def test_complete_inconvenient_catalogue(self):
        self.assertEqual(81, len(_INCONVENIENT_WORDS))
        self.assertEqual(81, len(set(_INCONVENIENT_WORDS)))
        for prefix in _INCONVENIENT_WORDS:
            value = _synthetic_curp(prefix)
            for cls in (MEX.CURP, MEX.NationalID):
                with self.subTest(prefix=prefix, cls=cls):
                    self.assertTrue(cls.checksum(value))
                    self.assertFalse(cls.validate(value))
                    self.assertIsNone(cls.parse(value))

    def test_complete_catalogue_second_letter_replacements(self):
        # RENAPO's printed page 7 requires replacing the second letter with X.
        for prefix in _INCONVENIENT_WORDS:
            value = _synthetic_curp(prefix[0] + 'X' + prefix[2:])
            for cls in (MEX.CURP, MEX.NationalID):
                with self.subTest(prefix=prefix, cls=cls):
                    self.assertTrue(cls.checksum(value))
                    self.assertTrue(cls.validate(value))
                    self.assertEqual(_expected_parse(value), cls.parse(value))

    def test_reported_inconvenient_prefix_examples(self):
        # Reported in issue #352; checksum-correct, but not valid CURP prefixes.
        for value in ('BUEI560427HVZRRL05', 'PUTA560427HVZRRL09'):
            for cls in (MEX.CURP, MEX.NationalID):
                with self.subTest(value=value, cls=cls):
                    self.assertTrue(cls.checksum(value))
                    self.assertFalse(cls.validate(value))
                    self.assertIsNone(cls.parse(value))

    def test_fixed_replacement_and_normal_probes(self):
        # Synthetic corrected probes, not issued ID examples.
        for value in ('BXEI560427HVZRRL04', 'PXTA560427HVZRRL08', _synthetic_curp('HEGG')):
            for cls in (MEX.CURP, MEX.NationalID):
                with self.subTest(value=value, cls=cls):
                    self.assertTrue(cls.checksum(value))
                    self.assertTrue(cls.validate(value))
                    self.assertEqual(_expected_parse(value), cls.parse(value))

    def test_gender_century_and_all_locations_unchanged(self):
        locations = (
            'AS BC BS CC CH CL CM CS DF DG GR GT HG JC MC MN MS NE NL NT OC PL QR QT '
            'SL SP SR TC TL TS VZ YN ZS'
        ).split()
        self.assertEqual(33, len(locations))
        for gender in 'HMX':
            for serial in '0A':
                for location in locations:
                    value = _synthetic_curp('BXEI', gender=gender, location=location, serial=serial)
                    for cls in (MEX.CURP, MEX.NationalID):
                        with self.subTest(value=value, cls=cls):
                            self.assertTrue(cls.checksum(value))
                            self.assertTrue(cls.validate(value))
                            self.assertEqual(_expected_parse(value), cls.parse(value))

    def test_existing_semantic_rejections(self):
        for value in (_synthetic_curp('BXEI', birth='560431'), _synthetic_curp('PXTA', location='XX')):
            for cls in (MEX.CURP, MEX.NationalID):
                with self.subTest(value=value, cls=cls):
                    self.assertTrue(cls.checksum(value))
                    self.assertFalse(cls.validate(value))
                    self.assertIsNone(cls.parse(value))
        for cls in (MEX.CURP, MEX.NationalID):
            self.assertFalse(cls.checksum('BXEI560427HVZRRL05'))
            self.assertFalse(cls.validate('BXEI560427HVZRRL05'))
            self.assertIsNone(cls.parse('BXEI560427HVZRRL05'))

    def test_malformed_input_contract(self):
        valid = 'BXEI560427HVZRRL04'
        inputs = (None, 123, 1.5, True, [], {}, b'BXEI560427HVZRRL04', '', valid[:-1], valid + '0',
                  valid + '\n', valid.lower(), 'ＢXEI560427HVZRRL04', 'BXEI５60427HVZRRL04',
                  'BXEI٥60427HVZRRL04', ' ' + valid, valid + ' ')
        for value in inputs:
            for cls in (MEX.CURP, MEX.NationalID):
                with self.subTest(value=value, cls=cls):
                    self.assertFalse(cls.validate(value))
                    self.assertIsNone(cls.parse(value))
                    self.assertFalse(cls.checksum(value))


if __name__ == '__main__':
    main()
