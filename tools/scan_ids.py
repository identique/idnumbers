import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Dict, List


from idnumbers.registry import list_supported_countries


def collect_ids(package_name: str, output_filename: str) -> None:
    """
    Dump the METADATA of every non-alias ID class into a JSON file.

    The classes come from the country registry (``idnumbers.registry.list_supported_countries``), one entry for each
    module that defines them, so the shared Yugoslav base class and the alias names are not listed.
    """
    # Import the package first so a wrong package name fails with a clear error
    importlib.import_module(package_name)

    modules: Dict[str, Dict[str, Any]] = {}
    classes_count = 0
    for entry in list_supported_countries():
        for cls in entry.id_types:
            # Work on a copy: the live METADATA, shared with the library, must stay unchanged
            cls_metadata = dict(vars(cls.METADATA))
            cls_metadata['regexp'] = cls_metadata['regexp'].pattern
            cls_metadata['masks'] = list(cls_metadata['masks'])
            alias_of = cls_metadata['alias_of']
            cls_metadata['alias_of'] = None if alias_of is None else alias_of.__name__
            module = modules.setdefault(cls.__module__, {
                'package_name': cls.__module__,
                'country_code': cls.__module__.split('.')[2],
                'ids': []
            })
            module['ids'].append({
                'class_name': cls.__name__,
                'metadata': cls_metadata
            })
            classes_count += 1

    metadata: List[Dict[str, Any]] = list(modules.values())
    country_codes = {module['country_code'] for module in metadata}
    print('----------------------------------------------------------------------------')
    print(f'Modules: {len(metadata)}')
    print(f'Countries: {len(country_codes)}')
    print(f'IDs: {classes_count}')
    print('----------------------------------------------------------------------------')
    # Write the metadata to a JSON file
    with open(output_filename, 'w') as f:
        json.dump(metadata, f, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pkg', nargs='?', help='the package to parse')
    parser.add_argument('output_file', nargs='?', help='path to the output JSON file')
    parser.add_argument('--markdown-dir', type=Path)
    parser.add_argument('--failure-reasons-file', type=Path)
    parser.add_argument('--input-formats-file', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if bool(args.pkg) != bool(args.output_file):
        parser.error('package and JSON output must be supplied together')
    if args.pkg is None and not any((args.markdown_dir, args.failure_reasons_file, args.input_formats_file)):
        parser.error('supply a package/JSON output or a Markdown output option')
    if args.check and args.output_file is not None:
        parser.error('--check applies only to generated Markdown, not JSON output')
    if args.pkg is not None:
        collect_ids(args.pkg, args.output_file)
    if any((args.markdown_dir, args.failure_reasons_file, args.input_formats_file)):
        from tools.generate_docs import generate

        generate(args.markdown_dir, args.failure_reasons_file, args.input_formats_file, args.check)
