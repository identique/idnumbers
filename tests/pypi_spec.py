from idnumbers.nationalid import AUS, NGA, ZAF


def validate_test():
    # Verify AUS tax file number (with checksum code)
    taxfile_number = '32547689'
    is_valid = AUS.TaxFileNumber.validate(taxfile_number)
    assert is_valid
    if is_valid:
        print(f'{taxfile_number} is a valid AUS Tax File Number')
    else:
        print(f'{taxfile_number} is an invalid AUS Tax File Number')

    # Verify AUS driver license number
    driver_license = '12 345 678'
    is_valid = AUS.DriverLicenseNumber.validate(driver_license)
    assert is_valid
    if is_valid:
        print(f'{driver_license} is a valid AUS Driver License Number')
    else:
        print(f'{driver_license} is an invalid AUS Driver License Number')

    # Verify AUS Medicare number (with checksum code)
    medicare_number = '2123 45670 1'
    is_valid = AUS.MedicareNumber.validate(medicare_number)
    assert is_valid
    if is_valid:
        print(f'{medicare_number} is a valid AUS Medicare Number')
    else:
        print(f'{medicare_number} is an invalid AUS Medicare Number')

    # Verify NGA national id number
    nga_nationalid = '12345678901'
    is_valid = NGA.NationalID.validate(nga_nationalid)
    assert is_valid
    if is_valid:
        print(f'{nga_nationalid} is a valid Nigerian National ID Number')
    else:
        print(f'{nga_nationalid} is an invalid Nigerian National ID Number')

    # Verify ZAF nation id number
    zaf_nationalid = '7605300675088'
    is_valid = ZAF.NationalID.validate(zaf_nationalid)
    assert is_valid
    if is_valid:
        print(f'{zaf_nationalid} is a valid South African ID Number')
    else:
        print(f'{zaf_nationalid} is an invalid South African ID Number')


def parse_test():
    id_number = '7605300675088'
    id_data = ZAF.NationalID.parse(id_number)
    assert id_data is not None

    # Access the date of birth
    print(f'Date of birth: {id_data["yyyymmdd"]}')

    # Access the gender
    print(f'Gender: {id_data["gender"]}')

    # Access the citizenship
    print(f'Citizenship: {id_data["citizenship"]}')


if __name__ == '__main__':
    print('run validate test')
    validate_test()
    print('run parse test')
    parse_test()
