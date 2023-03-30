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

## Use properties

The METADATA is build from [SimpleNamespace](https://docs.python.org/3/library/types.html#types.SimpleNamespace). We could use the following syntax to access them:

```python
from idnumbers.nationalid.NZL import InlandRevenueDepartmentNumber

# to access the metadata object
metadata = InlandRevenueDepartmentNumber.METADATA

# to access the metadata property
parsable = InlandRevenueDepartmentNumber.METADATA.parsable

# to access the metadata property with getattr to be backward-compatible
getattr(InlandRevenueDepartmentNumber.METADATA, 'checksum', False)

```
