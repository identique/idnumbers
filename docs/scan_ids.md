# Scan IDs tool

We create a new tool for dumping the metadata of all non-alias IDs into JSON.

We could run it with the following command:
```commandline
python -m tools.scan_ids
```

The result looks like:
```json
[
  {
    "package_name": "idnumbers.nationalid.yugoslavia",
    "country_code": "yugoslavia",
    "ids": [
      {
        "class_name": "UniqueMasterCitizenNumber",
        "metadata": {
          "iso3166_alpha2": null,
          "min_length": 13,
          "max_length": 13,
          "parsable": true,
          "checksum": true,
          "regexp": "^(?P<dd>\\d{2})(?P<mm>\\d{2})(?P<yyy>\\d{3})(?P<location>\\d{2})(?P<sn>\\d{3})(?P<checksum>\\d)$",
          "alias_of": null,
          "names": [
            "Unique  master citizen number",
            "JMBG",
            "Jedinstveni mati\u010dni broj gra\u0111ana",
            "\u0408\u0435\u0434\u0438\u043d\u0441\u0442\u0432\u0435\u043d\u0438 \u043c\u0430\u0442\u0438\u0447\u043d\u0438 \u0431\u0440\u043e\u0458 \u0433\u0440\u0430\u0452\u0430\u043d\u0430",
            "\u0408\u041c\u0411\u0413",
            "\u0415\u0434\u0438\u043d\u0441\u0442\u0432\u0435\u043d \u043c\u0430\u0442\u0438\u0447\u0435\u043d \u0431\u0440\u043e\u0458 \u043d\u0430 \u0433\u0440\u0430\u0453\u0430\u043d\u0438\u043d\u043e\u0442",
            "\u0415\u041c\u0411\u0413",
            "Enotna mati\u010dna \u0161tevilka ob\u010dana,",
            "EM\u0160O"
          ],
          "links": [
            "https://en.wikipedia.org/wiki/Unique_Master_Citizen_Number"
          ],
          "deprecated": false
        }
      }
    ]
  }
]
```

We could use the info/JSON to build a reference doc or generating the sample codes.
