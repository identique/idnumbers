"""Explicit, per-class limits of checksum detection on METADATA.example.

These are concrete synthetic witnesses, not country-wide exclusions. Tests require
exactly these accepted mutations and reject every other one, so the exception cannot
silently grow or outlive a fix. Reasons refer to the implementation under
idnumbers/nationalid/<country>/; no runtime or validity changes are made here.
"""

from typing import Dict, Tuple

SINGLE_DIGIT_CHANGE_UNDETECTED: Dict[str, Tuple[str, ...]] = {
    # medicare.py: validate compares normalized[8]; issue digit is not checksummed
    'idnumbers.nationalid.aus.medicare.MedicareNumber': (
        '2123 45670 0',
        '2123 45670 2',
        '2123 45670 3',
        '2123 45670 4',
        '2123 45670 5',
        '2123 45670 6',
        '2123 45670 7',
        '2123 45670 8',
        '2123 45670 9',
    ),
    # unifed_id_code.py: checksum retries mod 11 with different weights
    'idnumbers.nationalid.bgr.unifed_id_code.UnifiedIdCode': (
        '123456736',
    ),
    # dic.py: modulus_overflow_mod10 folds mod 11 onto ten values
    'idnumbers.nationalid.cze.dic.TaxNumber': (
        '65123891',
        '28123891',
        '25143891',
        '25120891',
        '25123491',
        '25123831',
    ),
    # personal_id.py: checksum retries mod 11 with different weights
    'idnumbers.nationalid.est.personal_id.PersonalID': (
        '47605030299',
    ),
    # icelandic_id.py: checksum excludes the century digit (numbers[0:-2])
    'idnumbers.nationalid.isl.icelandic_id.IcelandicID': (
        '120174-3390',
    ),
    # business_id.py: weight 11 is zero mod 11; retry uses shifted weights
    'idnumbers.nationalid.kaz.business_id.BusinessIDNumber': (
        '800140000003',
        '100140000013',
        '100140000023',
        '100140000033',
        '100140000043',
        '100140000053',
        '100140000063',
        '100140000073',
        '100140000083',
        '100140000093',
    ),
    # individual_id.py: weight 11 is zero mod 11; retry uses shifted weights
    'idnumbers.nationalid.kaz.individual_id.IndividualIDNumber': (
        '900101300007',
        '900101300027',
        '900101300037',
        '900101300047',
        '900101300057',
        '900101300067',
        '900101300077',
        '900101300087',
        '900101300097',
    ),
    # national_id.py: modulus_overflow_mod10 folds mod 11 onto ten values
    'idnumbers.nationalid.lka.national_id.NationalID': (
        '899001200001',
        '119001200001',
        '192001200001',
        '199601200001',
        '199081200001',
        '199003200001',
        '199001000001',
        '199001280001',
        '199001203001',
        '199001200401',
        '199001200061',
    ),
    # old_national_id.py: to_new delegates to the folded mod 11 new-ID checksum
    'idnumbers.nationalid.lka.old_national_id.OldNationalID': (
        '200120001V',
        '960120001V',
        '908120001V',
        '900320001V',
        '900100001V',
        '900123001V',
        '900120401V',
        '900120061V',
    ),
    # personal_code.py: checksum retries mod 11 with different weights
    'idnumbers.nationalid.ltu.personal_code.PersonalCode': (
        '39006010077',
    ),
    # curp.py: weights share factors with modulus 10
    'idnumbers.nationalid.mex.curp.CURP': (
        'HEGG060427MVZRRL04',
        'HEGG560407MVZRRL04',
        'HEGG560417MVZRRL04',
        'HEGG560427MVZRRL54',
    ),
    # national_id.py: modulus_overflow_mod10 folds mod 11 onto ten values
    'idnumbers.nationalid.tha.national_id.NationalID': (
        '3-1410-12345-67-3',
        '3-1610-12345-67-3',
        '3-1910-12345-67-3',
    ),
    # national_id.py: weights share factors with modulus 10
    'idnumbers.nationalid.twn.national_id.NationalID': (
        'A128456789',
        'A123056789',
        'A123256789',
        'A123656789',
        'A123856789',
        'A123406789',
        'A123456289',
    ),
    # entity_id.py: prefix changes weight series, and mod 11 has a second pass
    'idnumbers.nationalid.ukr.entity_id.EntityIDNumber': (
        '82000001',
        '32000071',
    ),
    # national_id.py: get_checksum excludes the trailing district digits
    'idnumbers.nationalid.zwe.national_id.NationalID': (
        '63123456B12',
        '63123456B22',
        '63123456B32',
        '63123456B42',
        '63123456B00',
        '63123456B03',
        '63123456B04',
        '63123456B05',
        '63123456B06',
        '63123456B07',
        '63123456B08',
    ),
}
