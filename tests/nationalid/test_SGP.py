from unittest import TestCase, main

from idnumbers.nationalid import SGP

_FORMSG_WEIGHTS = (2, 7, 6, 5, 4, 3, 2)
_FORMSG_ENCODINGS = {
    # (start constant, check letter table) for isNricValid
    'S': (0, 'JZIHGFEDCBA'),
    'T': (4, 'JZIHGFEDCBA'),
    'F': (0, 'XWUTRQPNMLK'),
    'G': (4, 'XWUTRQPNMLK'),
}
_FORMSG_M_ENCODING = 'KLJNPQRTUWX'


def _formsg_valid(id_number: str) -> bool:
    """
    Independent reference implementation of the GovTech FormSG checks, for cross-checking the library:
    https://github.com/opengovsg/FormSG/blob/develop/packages/shared/utils/nric-validation.ts
    isNricValid (S, T, F, G) and isMFinSeriesValid (M). Input must be upper case.
    """
    if len(id_number) != 9 or not id_number[1:8].isdigit() or not ('A' <= id_number[8] <= 'Z'):
        return False
    series, checksum = id_number[0], id_number[8]
    weighted = sum(w * int(d) for w, d in zip(_FORMSG_WEIGHTS, id_number[1:8]))
    if series in _FORMSG_ENCODINGS:
        start, encoding = _FORMSG_ENCODINGS[series]
        return checksum == encoding[(start + weighted) % 11]
    if series == 'M':
        # S1 = 3 + weighted sum, R1 = S1 % 11, P = 11 - R1, letter = encoding[P - 1]
        return checksum == _FORMSG_M_ENCODING[11 - (3 + weighted) % 11 - 1]
    return False


class TestSGPValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(SGP.NationalID.validate('S8076606H'))
        self.assertTrue(SGP.NationalID.validate('S1728872E'))
        self.assertTrue(SGP.NationalID.validate('G4549883U'))
        self.assertTrue(SGP.NationalID.validate('G4552218R'))
        self.assertTrue(SGP.NationalID.validate('S2111122H'))

    def test_error_case(self):
        self.assertFalse(SGP.NationalID.validate('S1179607H'))
        self.assertFalse(SGP.NationalID.validate('X1728872E'))

    def test_m_series(self):
        # vectors from issue #309; M1234567K is the FormSG isMFinSeriesValid test vector
        self.assertTrue(SGP.NationalID.validate('M1234567K'))
        self.assertTrue(SGP.NationalID.validate('M3960741N'))
        # N was the check letter of the old algorithm, which lacked the +3 start constant
        self.assertFalse(SGP.NationalID.validate('M1234567N'))

    def test_series_vectors(self):
        # vectors computed with the FormSG reference rules (see _formsg_valid), then pinned
        valid = [
            'S0000000J', 'S1234567D',
            'T0000000G', 'T1234567J',
            'F0000000X', 'F1234567N',
            'G0000000R', 'G1234567X',
        ]
        # same digits as a valid vector above, with a wrong check letter
        invalid = ['S0000000A', 'T0000000A', 'F0000000A', 'G0000000A']
        for series in 'STFG':
            self.assertEqual(2, len([v for v in valid if v[0] == series]))
            self.assertEqual(1, len([v for v in invalid if v[0] == series]))
        for code in valid:
            with self.subTest(code=code):
                self.assertTrue(SGP.NationalID.validate(code))
                self.assertTrue(_formsg_valid(code))
        for code in invalid:
            with self.subTest(code=code):
                self.assertFalse(SGP.NationalID.validate(code))
                self.assertFalse(_formsg_valid(code))

    def test_every_m_check_letter(self):
        # one valid vector per M-series check letter, computed with the FormSG reference rules;
        # M1234567K and M3960741N come from test_m_series
        vectors = [
            'M1234567K', 'M9207641L', 'M3745465J', 'M3960741N', 'M7675667P', 'M4088669Q',
            'M0886845R', 'M0258453T', 'M0634947U', 'M3818580W', 'M2512312X',
        ]
        letters = 'KLJNPQRTUWX'
        self.assertEqual(set(letters), {code[-1] for code in vectors})
        for code in vectors:
            with self.subTest(code=code):
                self.assertTrue(SGP.NationalID.validate(code))
                self.assertTrue(_formsg_valid(code))
                for other in letters:
                    if other != code[-1]:
                        self.assertFalse(SGP.NationalID.validate(code[:-1] + other), code[:-1] + other)

    def test_matches_formsg_reference(self):
        # deterministic sweep: about 1000 bodies x 5 series x 26 letters against the reference
        mismatches = []
        for n in range(0, 10_000_000, 9973):
            body = '%07d' % n
            for series in 'STFGM':
                for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    code = series + body + letter
                    if SGP.NationalID.validate(code) != _formsg_valid(code):
                        mismatches.append(code)
        self.assertEqual([], mismatches)


if __name__ == '__main__':
    main()
