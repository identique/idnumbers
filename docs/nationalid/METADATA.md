# METADATA of an ID

All ID validators/parsers have one class-based `METADATA` object for hinting users how to use it.

The `METADATA` structure are the same among all classes. If you find any inconsistency or insufficient, please [file a ticket](https://github.com/Identique/idnumbers/issues) and tag us, @microdataxyz.

## Data structure

| property name  | property type                                                                   | description                                                                                                   |
|----------------|---------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| iso3166_alpha2 | string                                                                          | The ISO 3166-2 code for the issuing country                                                                   |
| min_length     | int                                                                             | The minimum length of the ID                                                                                  |
| max_length     | int                                                                             | The maximum length of the ID                                                                                  |
| parsable       | boolean                                                                         | To indicate if we could parse information from ID. If it is true, the class supports `parse` function.        |
| checksum       | boolean                                                                         | To indicate if the ID supports checksum in its design. If it is true, the class supports `checksum` function. |
| regexp         | [Pattern](https://docs.python.org/3/library/re.html#regular-expression-objects) | The pattern object for validate the ID.                                                                       | 
| alias_of       | Python Cls                                                                      | The original class of this ID number. It is none if it is not an alias                                        |
| names          | Array of string                                                                 | The possible names we could see in the ID cards or other places.                                              |
| links          | Array of string                                                                 | The reference links of this ID                                                                                |
| deprecated     | boolean                                                                         | To indicate if the ID is deprecated by the country of not. New or Old version.                                |
| country_name   | string                                                                          | The English name of the issuing country, the same as in the [country registry](../../idnumbers/registry.py), such as `Taiwan`. |
| id_type        | string                                                                          | The English name of the kind of ID in Title Case, such as `Medicare Number`.                                  |
| official_name  | string or None                                                                  | The official name of the ID in the local language, such as `Henkilötunnus` or `國民身分證統一編號`. It is `None` when the ID has no local-language name, as with an ID that is named in English (the UK NINO, the US SSN, the Australian Medicare number). It is never the same as `id_type`. |
| display_format | string                                                                          | A human-readable layout of the ID, such as `###-##-####` or `YYMMDD-SSSC`.                                     |
| example        | string                                                                          | A synthetic ID that the class validates: constructed with a valid check digit, or a number documented as a sample by the issuing authority. It is not the number of a real person. It is written in the first (preferred) layout of `masks`. |
| checksum_algorithm | string or None                                                              | A short description of the algorithm that the `checksum` function computes, such as `Luhn (mod 10)`. It is `None` when `checksum` is false. |
| masks          | Tuple of string                                                                 | The layouts the class accepts, the preferred display layout first. See [the mask vocabulary](#mask-vocabulary). |

### Mask vocabulary

A mask describes one accepted layout of the ID, one character per character of the ID:

| character | meaning                                   |
|-----------|-------------------------------------------|
| `#`       | a digit                                   |
| `L`       | a letter                                  |
| `X`       | a letter or a digit                       |
| `*`       | any character except white space          |

Every other character of a mask is a separator, and it is one of space, `-`, `.`, `/`, `(` and `)`. A separator is part of the layout, so a validator that rejects separators has masks without them: the masks are layouts the class accepts, not the way an authority prints the ID. A mask has one slot for each character that the ID has without its separators, so the number of slots of a mask is a length between `min_length` and `max_length`. A slot that stands for a fixed character of the ID, such as the `U` of an Austrian UID, is written as the kind of character (`L`), not as the character.

The tests in `tests/test_metadata.py` check every ID class: the example is valid and written in the first mask, it is accepted when it is laid into every mask it fits, and every other mask has a test sample that the class accepts.

## Use properties

The METADATA is an `IdMetadata` (in `idnumbers/nationalid/metadata.py`), a subclass of [SimpleNamespace](https://docs.python.org/3/library/types.html#types.SimpleNamespace) that adds a type annotation for every property. It is still a `SimpleNamespace`, so attribute access, `vars()`, `copy.copy()` and `getattr()` work as before. We could use the following syntax to access the properties:

```python
from idnumbers.nationalid.NZL import InlandRevenueDepartmentNumber

# to access the metadata object
metadata = InlandRevenueDepartmentNumber.METADATA

# to access the metadata property
parsable = InlandRevenueDepartmentNumber.METADATA.parsable

# to access the metadata property with getattr to be backward-compatible
getattr(InlandRevenueDepartmentNumber.METADATA, 'checksum', False)

# the descriptive properties that the ID classes have since the typed IdMetadata
InlandRevenueDepartmentNumber.METADATA.id_type  # 'Inland Revenue Department Number'
InlandRevenueDepartmentNumber.METADATA.example  # '49-091-850'
InlandRevenueDepartmentNumber.METADATA.masks    # ('##-###-###', '###-###-###', '########', '#########')

```

### Formatting helpers and UI patterns

The primary-only [formatting helpers](../../README.md#primary-id-formatting-and-input-masks) consume `masks`;
`format_id()` chooses the first layout with a matching slot count, without validating characters or checksums.
`get_input_mask()` returns a frozen `InputMask` with tuple masks and a case-sensitive whole-input pattern.
Its `#`, `L` and `X` tokens deliberately restrict digits/letters to ASCII; `*` matches Unicode non-whitespace.
The pattern describes a UI layout, not all inputs the country validator accepts. Greece's primary example uses
accepted Latin `AB-123456`; Greek letters remain valid and format unchanged but intentionally fail the ASCII
`L` pattern. No transliteration is performed. Normalization does not change the country validators' handling of
compact inputs: measured on primary examples, CHE, CHL, KOR and USA reject compact text; all formatted examples
validate. See the [format API documentation](https://identique.github.io/idnumbers/idnumbers.format.html).
