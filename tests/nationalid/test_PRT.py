import inspect
from itertools import product
from unittest import TestCase, main

from idnumbers.nationalid import PRT


class TestPRTCivilIDNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(PRT.CivilIDNumber.validate('900000007'))
        self.assertTrue(PRT.CivilIDNumber.validate('118666070'))
        self.assertTrue(PRT.TaxIDNumber.validate('100000002'))

    def test_error_case(self):
        self.assertFalse(PRT.CivilIDNumber.validate('900000017'))
        self.assertFalse(PRT.CivilIDNumber.validate('11866607-0'))
        self.assertFalse(PRT.TaxIDNumber.validate('950000002'))


class TestPRTCitizenCard(TestCase):
    @staticmethod
    def card_number(body: str) -> str:
        # Synthetic checksum vectors, not evidence that a card has been issued.
        # Independent right-to-left implementation of AMA section 2.2 (printed page 4).
        total = 0
        for position, character in enumerate(reversed(body), start=1):
            value = int(character) if character.isdigit() else ord(character) - ord('A') + 10
            if position % 2 == 1:
                value *= 2
                if value >= 10:
                    value -= 9
            total += value
        return body + str((-total) % 10)

    def test_official_example(self):
        # AMA, Validação Número de Documento Cartão de Cidadão, printed page 4.
        for method in (PRT.CitizenCard.validate, PRT.CitizenCard.checksum):
            self.assertTrue(method('000000000ZZ4'))
            self.assertFalse(method('000000000ZZ3'))

    def test_all_version_characters_and_check_digit_mutations(self):
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for digits in ('000000000', '123456789', '900000007', '999999999'):
            for version in product(alphabet, repeat=2):
                number = self.card_number(digits + ''.join(version))
                with self.subTest(number=number):
                    for method in (PRT.CitizenCard.validate, PRT.CitizenCard.checksum):
                        self.assertTrue(method(number))
                        for digit in '0123456789':
                            if digit != number[-1]:
                                self.assertFalse(method(number[:-1] + digit))

    def test_malformed_input(self):
        invalid = (
            None, 0, False, 123456789, b'000000000ZZ4', [], {}, '',
            '00000000ZZ4', '0000000000ZZ4', '00000000 0 ZZ4', '000000000-ZZ4',
            ' 000000000ZZ4', '000000000ZZ4 ', '000000000ZZ4\n', '000000000ZZ4\r\n',
            '000000000zz4', '000000000Zz4', '000000000ZZX', '000000000_Z4',
            '０００００００００ZZ4', '٠٠٠٠٠٠٠٠٠ZZ4', '000000000ＺZ4', '000000000ZZ４',
            '00000000²ZZ4', '000000000ZZ4\x00', '000000000Z\n4',
        )
        for number in invalid:
            with self.subTest(number=number):
                self.assertFalse(PRT.CitizenCard.validate(number))
                self.assertFalse(PRT.CitizenCard.checksum(number))

    def test_metadata_and_api(self):
        metadata = PRT.CitizenCard.METADATA
        self.assertEqual(metadata.iso3166_alpha2, 'PT')
        self.assertEqual((metadata.min_length, metadata.max_length), (12, 12))
        self.assertFalse(metadata.parsable)
        self.assertTrue(metadata.checksum)
        self.assertIsNone(metadata.alias_of)
        self.assertFalse(metadata.deprecated)
        self.assertEqual(metadata.names, ['Citizen Card', 'Cartão de Cidadão', 'CC'])
        self.assertTrue(any('autenticacao.gov.pt' in link for link in metadata.links))
        self.assertIsNone(metadata.regexp.match('000000000ZZ4\n'))
        self.assertFalse(hasattr(PRT.CitizenCard, 'parse'))
        for name in ('validate', 'checksum'):
            self.assertIsInstance(inspect.getattr_static(PRT.CitizenCard, name), staticmethod)
            signature = inspect.signature(getattr(PRT.CitizenCard, name))
            self.assertEqual(list(signature.parameters), ['id_number'])
            self.assertIs(signature.parameters['id_number'].annotation, str)
            self.assertIs(signature.return_annotation, bool)

    def test_legacy_exports_stay_civil_only(self):
        from idnumbers.nationalid.prt.citizen_card import CitizenCard
        self.assertIs(PRT.CitizenCard, CitizenCard)
        for validator in (PRT.CivilIDNumber, PRT.NationalID):
            self.assertTrue(validator.validate('900000007'))
            self.assertTrue(validator.validate('118666070'))
            self.assertFalse(validator.validate('000000000ZZ4'))


class TestPRTTaxIDNumber(TestCase):
    @staticmethod
    def tax_number(prefix: str) -> str:
        # Synthetic numbers use the unchanged NIF weighted modulus checksum.
        body = prefix + '123456'
        remainder = sum(int(digit) * weight for digit, weight in zip(body, range(9, 1, -1))) % 11
        return body + str(0 if remainder < 2 else 11 - remainder)

    def test_new_prefixes(self):
        # Prefixes listed by ESMA MiFIR data reporting Q&A, printed page 65.
        # These checksum-correct examples are synthetic, not issued NIFs.
        numbers = ('741234564', '751234567', '771234562', '781234565', '791234568')
        for number in numbers:
            with self.subTest(number=number):
                self.assertEqual(self.tax_number(number[:2]), number)
                for method in (PRT.TaxIDNumber.validate, PRT.TaxIDNumber.checksum):
                    self.assertTrue(method(number))
                    self.assertFalse(method(number[:-1] + str((int(number[-1]) + 1) % 10)))

    def test_prefix_policy_is_otherwise_unchanged(self):
        accepted = ('10', '29', '39', '45', '50', '69', '70', '71', '72', '90', '91', '98', '99')
        rejected = ('00', '40', '46', '73', '76', '80', '89', '92', '97')
        for prefix in accepted + rejected:
            number = self.tax_number(prefix)
            with self.subTest(number=number):
                for method in (PRT.TaxIDNumber.validate, PRT.TaxIDNumber.checksum):
                    self.assertEqual(method(number), prefix in accepted)

    def test_metadata_names_and_source(self):
        self.assertEqual(PRT.TaxIDNumber.METADATA.names,
                         ['Tax ID Number', 'Número de identificação fiscal', 'NIF'])
        self.assertTrue(any('esma.europa.eu' in link for link in PRT.TaxIDNumber.METADATA.links))


if __name__ == '__main__':
    main()
