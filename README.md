# idnumbers

Welcome to the idnumbers project! Our goal is to provide a python3 library for verifying and parsing national ID
numbers. This library can be used to quickly and easily validate and extract information from ID numbers issued by
various countries. It is an open source project, so feel free to use and contribute to it.

* [![PyPI version](https://badge.fury.io/py/idnumbers.svg)](https://badge.fury.io/py/idnumbers)
* [![PyPI Stats](https://img.shields.io/pypi/dm/idnumbers)](https://pypistats.org/packages/idnumbers)

# Features

The idnumbers library offers the following features:

* Verification of national ID numbers: This feature allows you to check if a given ID number is valid and has been
  issued by the respective country.
* Parsing of national ID numbers: This feature allows you to extract useful information from an ID number such as the
  date of birth, gender, and more.
* Support for multiple countries: The library currently supports several countries, with more being added in the future.
* Easy to use and well-documented API: The library has a simple and intuitive API that makes it easy to use and
  well-documented for developers to understand.
* Lightweight and efficient: The library is lightweight, meaning it does not have many dependencies, and it is
  efficient, meaning it does not consume much memory or processing power.

# Installation

Installing idnumbers is easy! You can use pip, the package installer for Python, to install the latest version of the
library. Simply open a terminal and run the following command:

It is highly recommended to install the library in a virtual environment, this will prevent conflicts with other python
packages in your system. You can create a virtual environment using virtualenv or conda.

For virtualenv:

```shell
virtualenv <envname>
source <envname>/bin/activate
```

For Anaconda:

```shell
conda create --name <envname>
conda activate <envname>
```

Once you have activated your virtual environment, you can install idnumbers by running the following command:

```shell
pip install idnumbers
```

This will install the latest version of idnumbers and its dependencies.

You can also install a specific version of idnumbers by specifying the version number in the command, like this:

```shell
pip install idnumbers==<version>
```

Alternatively, you can install from source by cloning the git repository and installing it via

```shell
git clone https://github.com/Identique/idnumbers.git
cd idnumbers
pip install .
```

Please make sure you have the latest version of pip and setuptools installed before proceeding with the installation.

Once you have finished using the library, you can deactivate the virtual environment by running:

```shell
deactivate
```

or

```shell
conda deactivate
```

# Usage

## Verify National IDs

The idnumbers library makes it easy to verify national ID numbers. Here are some examples of how to use the library for
verifying ID numbers.

```python
from idnumbers.nationalid import AUS, NGA, ZAF

# Verify AUS tax file number (with checksum code)
taxfile_number = '32547689'
is_valid = AUS.TaxFileNumber.validate(taxfile_number)
if is_valid:
    print(f'{taxfile_number} is a valid AUS Tax File Number')
else:
    print(f'{taxfile_number} is an invalid AUS Tax File Number')

# Verify AUS driver license number
driver_license = '12 345 678'
is_valid = AUS.DriverLicenseNumber.validate(driver_license)
if is_valid:
    print(f'{driver_license} is a valid AUS Driver License Number')
else:
    print(f'{driver_license} is an invalid AUS Driver License Number')

# Verify AUS Medicare number (with checksum code)
medicare_number = '2123 45670 1'
is_valid = AUS.MedicareNumber.validate(medicare_number)
if is_valid:
    print(f'{medicare_number} is a valid AUS Medicare Number')
else:
    print(f'{medicare_number} is an invalid AUS Medicare Number')

# Verify NGA national id number
nga_nationalid = '12345678901'
is_valid = NGA.NationalID.validate(nga_nationalid)
if is_valid:
    print(f'{nga_nationalid} is a valid Nigerian National ID Number')
else:
    print(f'{nga_nationalid} is an invalid Nigerian National ID Number')

# Verify ZAF nation id number
zaf_nationalid = '7605300675088'
is_valid = ZAF.NationalID.validate(zaf_nationalid)
if is_valid:
    print(f'{zaf_nationalid} is a valid South African ID Number')
else:
    print(f'{zaf_nationalid} is an invalid South African ID Number')

```

These examples show how to use the idnumbers library to verify different types of national ID numbers for different
countries. The `validate` method returns a boolean value indicating if the ID number is valid or not. All modules under
nationalid package support the `validate` function.

You can also use the library to validate different types of ID numbers for different countries.

It is important to keep in mind that the library is only able to validate the format and the checksum of the ID number,
not if it is an actual issued ID number.

## Parse National IDs

The idnumbers library supports the parse function for certain national ID numbers, which allows you to easily extract
detailed information from the ID number. The parse function is only available for national IDs for which the
METADATA.parsable field is set to True.

For example, the South African ID Number, Nigerian National ID Number and Australian Medicare Number all support the
parse function. By using the parse method, you can extract information such as the date of birth, gender, and
citizenship from these ID numbers.

Here is an example of how to use the parse function for a South African ID number:

```python
from idnumbers.nationalid import ZAF

# Parse the national ID number
id_number = '7605300675088'
id_data = ZAF.NationalID.parse(id_number)

# Access the date of birth
print(f'Date of birth: {id_data["yyyymmdd"]}')

# Access the gender
print(f'Gender: {id_data["gender"]}')

# Access the citizenship
print(f'Citizenship: {id_data["citizenship"]}')
```

This example shows how to use the parse method of the ZAF.NationalID class to extract the date of birth, gender and
citizenship from a South African ID number. The parse method returns a dictionary with various fields,
including `yyyymmdd` for date of birth, `gender` for gender and `citizenship` for citizenship.

Similarly, you can parse the Nigerian National ID Number and Australian Medicare Number by using the
NGA.NationalID.parse() and AUS.MedicareNumber.parse() respectively.

Please note that the returned parsed data may vary depending on the country and id type you are using. Also, it is
important to keep in mind that the library is only able to validate the format and the checksum of the ID number, not if
it is an actual issued ID number.

# Supported Countries

Here's the list of the countries we have
implemented [Country List](https://identique.github.io/idnumbers/idnumbers/nationalid.html)

# Contribution

The idnumbers project is an open-source project and contributions from the community are always welcome. There are
several ways you can contribute to the project:

1. **Use the library**: The best way to contribute to the project is by using the library and providing feedback. This
   will help us understand how the library is being used and identify areas for improvement.
2. **Raise feature requests**: If you have an idea for a new feature or an improvement,
   please [raise an issue](https://github.com/identique/idnumbers/issues/new/choose) on GitHub.
   This will allow us to discuss the feature and plan its implementation.
3. **Implement new ID number parsers or validators**: The library currently supports several countries, but there is
   always room for more. If you want to add support for a new country, you can submit a pull request with the
   implementation. Before that, please raise
   a [new ID number reqeust](https://github.com/identique/idnumbers/issues/new?assignees=microdataxyz&labels=enhancement&template=new-national-id-requests.md&title=%5BNationalID%5D)
   to us.
4. **Report bugs**: If you find a bug in the library, please
   raise [an issue](https://github.com/identique/idnumbers/issues/new?assignees=microdataxyz&labels=bug%2C+enhancement&template=bug_report.md&title=%5BBUG%5D+XXX+country+issue)
   on GitHub with a detailed description of the
   problem.
5. **Improve documentation**: The library has a [well-documented API](https://identique.github.io/idnumbers/), but
   there is always room for improvement. If you
   find any errors or inconsistencies in the documentation, you can submit a pull request with the changes.

We appreciate any contributions, big or small, and we are always looking for ways to improve the library. If you have
any questions or need help getting started, please feel free to reach out to us.

# License

The idnumbers project is released in [MIT license](https://github.com/identique/idnumbers/blob/main/LICENSE).

# Thank You!
The idnumbers project provides a python3 library for verifying and parsing national ID numbers. It supports multiple countries and provides a simple and well-documented API. The library is open-source, and contributions from the community are always welcome. Whether you're using the library and providing feedback, raising feature requests, implementing new ID number parsers or validators or reporting bugs, you're helping the project to be better.

Thank you for considering using idnumbers in your project. We hope it will be useful for you and we are looking forward to your feedback and contributions
