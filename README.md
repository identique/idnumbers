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

See the [changelog](https://github.com/identique/idnumbers/blob/main/CHANGELOG.md) for the changes in each release.

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

## Using idnumbers with uv

Install [uv](https://docs.astral.sh/uv/) first, then choose the workflow that fits your use case.

### Project dependency

From an existing uv project directory:

```shell
uv add idnumbers
```

For a new project, first run:

```shell
uv init idnumbers-example
cd idnumbers-example
```

Then run `uv add idnumbers` to record the dependency and update the project's environment and lockfile.

### Existing virtual environment

In an activated virtual environment, or a directory containing `.venv`:

```shell
uv pip install idnumbers
```

If you need a new environment, run `uv venv` first. To install a specific released version instead:

```shell
uv pip install idnumbers==1.13.0
```

### One-off validation

```shell
uvx --with idnumbers python -c "from idnumbers.nationalid import TWN; print(TWN.NationalID.validate('A123456789'))"
```

This prints `True`. uv installs the dependency in a temporary uv-managed isolated environment, without adding it to
an existing project's dependencies or requiring a manually activated environment. Validation checks format and
checksum, not whether an ID was issued.

### Standalone script

Save this as `uv_example.py`. The [PEP 723](https://peps.python.org/pep-0723/) metadata declares its Python requirement
and dependency:

```python
# /// script
# requires-python = ">=3.9"
# dependencies = ["idnumbers"]
# ///

from idnumbers.nationalid import TWN

id_number = "A123456789"
print(TWN.NationalID.validate(id_number))
print(TWN.NationalID.parse(id_number))
```

Run it with:

```shell
uv run uv_example.py
```

uv reads the metadata and manages an isolated environment for the script. See the
[uv scripts guide](https://docs.astral.sh/uv/guides/scripts/) for details. The runnable
[companion example](docs/examples/uv_script.py) validates and parses three countries and fails if any result is
unexpected. From this checkout, run `uv run docs/examples/uv_script.py`.

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

### Input handling

- `validate()` returns a `bool` for any input and is not meant to raise. Anything that is not a `str` (`None`, numbers,
  `bytes`, lists, ...) gives `False`, an integer is never converted to a string, so `validate(37605030299)` is `False`.
- The whole string must match the ID format. Nothing is stripped, so surrounding whitespace or a trailing newline gives
  `False` (the Irish PPS number is the one exception: its own format allows one trailing space).
- Only ASCII digits `0-9` are accepted, other Unicode digits such as `١٢٣` or `１２３` give `False`.
- Separators and letter case are type specific. Several ID types accept their usual written form (for example spaces,
  dashes or dots inside the number, as in `8924 7352 8038`), and a few accept lower case letters. Most types are case
  sensitive. The `METADATA.regexp` of each type shows the accepted written form. A few types (for example the Czech
  `TaxNumber`, which drops every `/` anywhere in the input before matching) also normalize the input before checking
  it, so for those the regexp alone does not show everything they accept.
- `parse()` returns `None` for invalid input.

## Parse a primary ID by country

`parse_id_info(country, id_number)` uses the same country lookup and validation as `idnumbers.validate()`,
selecting only the country's primary `NationalID`. It returns a frozen `ParseSuccess` or `ParseFailure`; use
`result.ok` or `isinstance(result, ParseSuccess)` to narrow the result in typed code.

```python
from idnumbers import FailureReason, ParseSuccess, parse_id_info

result = parse_id_info('tw', 'A123456789')
if result.ok:
    print(result.country_code, result.info['gender'])
else:
    print(result.reason, result.error_message)
assert isinstance(result, ParseSuccess)

# A valid primary ID need not contain extractable information.
result = parse_id_info('us', '012-12-0928')
assert not result.ok and result.reason == FailureReason.NOT_PARSABLE
print(result.reason.value)
```

On success, `country_code` is the resolved alpha-3 code and `info` is a fresh shallow dictionary matching the
country class's `parse()` output, including its date and enum values. Result fields are frozen, but the dictionary
itself is not immutable. The supplied `id_number` is preserved without normalization.

An unknown or non-string country gives `UNSUPPORTED_COUNTRY` with `country_code=None`. Invalid IDs have the same
reason as `validate()` (best-effort granular reasons). A valid ID with no parser, or a parser returning `None`, gives
`NOT_PARSABLE`. Validator/parser exceptions give `VALIDATION_FAILED` with `error_message` formatted as
`ExceptionType: message`; this entry point does not raise. Failure results have `reason` and `error_message`, not
`info`. The existing country-specific `Cls.parse()` methods and their return types are unchanged; use those classes
when you need a secondary ID type.

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

## Look up a country

When the country is only known at run time, for example from a form field, the country registry finds the validator for
you. The lookup functions accept an ISO 3166-1 alpha-2 or alpha-3 code in any letter case, and return `None` for
anything they don't know instead of raising an error. The registry imports a country module the first time it is
needed, so `import idnumbers` stays fast. `register()` adds a custom country to the registry.

```python
import idnumbers

# Find the validator of a country by its alpha-2 or alpha-3 code, in any letter case
validator = idnumbers.get_validator('tw')
print(validator.validate('A123456789'))

# Describe a country
australia = idnumbers.get_country('AUS')
print(australia.name, australia.alpha2)
print([id_type.__name__ for id_type in australia.id_types])

# An unknown country gives None
print(idnumbers.get_validator('XX') is None)

# List the supported countries
print(len(idnumbers.list_supported_countries()))
```

`get_country()` returns a `CountryEntry` with the `alpha3` and `alpha2` codes, the English `name`, the `national_id`
class of the country and all its `id_types`. `resolve_country()` only turns a code into the alpha-3 code and imports
nothing.

## Validate by country

`validate()` checks an ID number of any supported country in one call. It takes the code of the country and the ID
number, and returns a `ValidationResult` with `is_valid`, the alpha-3 `country_code`, the `id_number` as you passed it,
the `extracted_info` of a valid ID number whose type can be parsed, and a `reason` for a failure. A result is truthy
when it is valid, and `validate()` never raises: an unknown country or a malformed ID number gives an invalid result.
Reasons are best effort: `invalid_length`, `invalid_format`, `checksum_mismatch` and `invalid_birthdate` are derived
from metadata, definite checksum mismatches and traced calendar checks, in that order. Inconclusive checks and
validator/parser exceptions retain `validation_failed`. The country classes and their validity rules are unchanged.
The enum is non-exhaustive: callers should handle unknown future reasons with a generic fallback.

```python
from idnumbers import validate, validate_many

# A valid ID number, with the data parsed from it
result = validate('tw', 'A123456789')
print(result.is_valid, result.country_code, result.extracted_info['gender'])

# An invalid result is falsy and says why
print(bool(validate('tw', 'A123456780')))

# An unsupported country is reported, not raised
print(validate('XX', 'A123456789').reason.value)

# Validate several ID numbers, each with its own country
print([result.is_valid for result in validate_many([('tw', 'A123456789'), ('XX', '1')])])
```

### Explain a failure of any ID type

`failure_reason(id_class, id_number)` also supports secondary types. It returns `None` for a valid ID and never raises.
For diagnosis only, it considers both the original input and a candidate with whitespace and `. - / ( )` removed.
This does **not** normalize validation input or make a rejected ID valid. A computed checksum without a named
`checksum` regexp group is inconclusive, so it retains the generic reason rather than guessing.

```python
from idnumbers import FailureReason, failure_reason, validate
from idnumbers.nationalid import AUS

assert validate('TW', 'A12345').reason == FailureReason.INVALID_LENGTH
assert validate('TW', 'A123456788').reason == FailureReason.CHECKSUM_MISMATCH
assert validate('ZA', '7602300675085').reason == FailureReason.INVALID_BIRTHDATE
assert failure_reason(AUS.MedicareNumber, '2123 45670 1') is None
print(validate('TW', 'A12345').reason.value)
```

# Supported Countries

Here's the list of the countries we have
implemented [Country List](https://identique.github.io/idnumbers/idnumbers/nationalid.html).
The `list_supported_countries()` function returns them at run time.

# Metadata Structure of each ID

Here's the metadata definitions and how to use it in idnumbers: [METADATA](https://github.com/identique/idnumbers/blob/main/docs/nationalid/METADATA.md)

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
