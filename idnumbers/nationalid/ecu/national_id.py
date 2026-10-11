import re
from ..metadata import IdMetadata
from typing import Optional, TypedDict
from ..util import CHECK_DIGIT, luhn_digit, match_regexp


class ParseResult(TypedDict):
    """The parse result of Ecuador cédula de identidad"""
    province: str
    """the first 2 digits: the province code ``01``-``24``, or ``30`` for a cédula registered abroad"""
    sequence_number: str
    """digits 4 to 9, the sequence number"""
    checksum: CHECK_DIGIT
    """the last digit: the mod-10 check digit of the first nine digits"""


class NationalID:
    """
    Ecuador cédula de identidad (also called cédula de ciudadanía), issued by the Dirección General de Registro
    Civil, Identificación y Cedulación.

    The number has 10 digits, ``PPTSSSSSSC``: a 2-digit province code ``PP``, a third digit ``T``, a 6-digit
    sequence number ``SSSSSS`` and a check digit ``C``. ``validate()`` checks the following:

    - **Province:** ``01`` to ``24``, or ``30``. Code ``30`` ("Exterior") was created by Registro Civil Resolution
      140 (Registro Oficial No. 681, 12 April 2012) for Ecuadorians born abroad and registered by consulates; the
      Secretaría Nacional de la Administración Pública states that it is as valid as the series ``01`` to ``24``.
      The province names are not decoded.
    - **Third digit:** ``0`` to ``6`` for the provinces ``01`` to ``24``. The Gob.EC / MINTEL issue tracker lists
      reported cédulas with the third digit 6 that the forms failed to validate, so 6 is accepted. For a consular
      cédula (province ``30``) the third digit can only be ``4`` or ``5``.
    - **Check digit:** mod 10 with weights 2,1,2,1,2,1,2,1,2 over the first nine digits, a product above 9 minus 9
      (the Luhn rule), so the check digit is ``(10 - sum % 10) % 10``.
    - **Separator:** one optional hyphen right before the check digit, ``171430710-3``, as printed in
      python-stdnum's examples. No other separator is accepted.

    Deliberately different from other libraries:

    - python-stdnum also accepts province ``50`` and any third digit for province ``30`` (for example
      ``5010000007`` and ``3000000004``). No official source was found for either, so they are rejected here.
    - The Node port rejects the third digit 6, which is accepted here (for example the synthetic ``0960000008``).

    Sources:

    - Secretaría Nacional de la Administración Pública, "Instructivo para agregar los números de cédula que inician
      con el número 30, en los Portales Web Gubernamentales Homologados" (September 2015). It lists the public
      test cédulas ``3040040382``, ``3040123386``, ``3044223182``, ``3043223183`` and ``3042233274``:
      https://esacc.corteconstitucional.gob.ec/storage/api/v1/10_DWL_FL/e2NhcnBldGE6J2VzY3JpdG8nLCB1dWlkOicxODMyYTNhZC1hMzRiLTQ0MTUtYTNhYi0wNmEwMWYwYTdhZmQucGRmJ30=
    - Gob.EC / MINTEL issue 597, the third digit of the cédula: https://minka.gob.ec/mintel/ge/rutr/gobec/-/issues/597
    - python-stdnum, ``stdnum/ec/ci.py``: https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ec/ci.py
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'EC',
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<province>0[1-9]|1\d|2[0-4]|30)(?P<third>\d)(?P<sequence_number>\d{6})-?'
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['Cédula de Identidad',
                  'Cédula de Ciudadanía',
                  'Cédula'],
        'links': ['https://esacc.corteconstitucional.gob.ec/storage/api/v1/10_DWL_FL/'
                  'e2NhcnBldGE6J2VzY3JpdG8nLCB1dWlkOicxODMyYTNhZC1hMzRiLTQ0MTUtYTNhYi0wNmEwMWYwYTdhZmQucGRmJ30=',
                  'https://minka.gob.ec/mintel/ge/rutr/gobec/-/issues/597',
                  'https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ec/ci.py'],
        'deprecated': False,
        'country_name': 'Ecuador',
        'id_type': 'Identity Card Number',
        'official_name': 'Cédula de Identidad',
        'display_format': '##########',
        'example': '1710000009',
        'checksum_algorithm': 'Mod 10 with weights 2,1,2,1,2,1,2,1,2 over the first nine digits (Luhn)',
        'masks': ('##########', '#########-#')
    })
    """metadata of this id"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the province, the third digit and the check digit"""
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result; ``None`` unless the number is valid"""
        match_obj = match_regexp(id_number, NationalID.METADATA.regexp)
        if not match_obj:
            return None
        province = match_obj.group('province')
        third = match_obj.group('third')
        allowed_third = '45' if province == '30' else '0123456'
        if third not in allowed_third:
            return None
        checksum = NationalID.checksum(id_number)
        if checksum is None or str(checksum) != match_obj.group('checksum'):
            return None
        return {
            'province': province,
            'sequence_number': match_obj.group('sequence_number'),
            'checksum': checksum,
        }

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """
        calculate the mod-10 check digit from the first nine digits

        :return: the expected check digit, or ``None`` if the layout does not match. The number's own last digit
            and the third-digit rule are not applied; ``validate()`` does that.
        """
        match_obj = match_regexp(id_number, NationalID.METADATA.regexp)
        if not match_obj:
            return None
        digits = match_obj.group('province') + match_obj.group('third') + match_obj.group('sequence_number')
        return luhn_digit([int(char) for char in digits], multipliers_start_by_two=True)
