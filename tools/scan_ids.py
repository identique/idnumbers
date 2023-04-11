import importlib
import inspect
import json
import os


def collect_ids(package_name, output_filename):
    # Find the root package directory
    package_directory = importlib.import_module(package_name).__path__[0]

    # Recursively collect metadata for all modules and classes
    metadata = []
    modules_count = 0
    classes_count = 0
    country_codes = []
    for root, _, files in os.walk(package_directory):
        for file in files:
            if file.endswith('.py'):
                # Convert the file path to a package path
                module_name = os.path.splitext(os.path.relpath(os.path.join(root, file), package_directory))[0]
                module_name = module_name.replace(os.path.sep, '.')
                # No upper case module name. They are aliases
                if module_name == module_name.upper():
                    continue

                # Import the module and collect metadata for its classes
                module = importlib.import_module(package_name + '.' + module_name)
                module_metadata = []
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, 'METADATA') and obj.METADATA.alias_of is None:
                        cls_metadata = obj.METADATA.__dict__
                        if type(cls_metadata['regexp']) is not str:
                            cls_metadata['regexp'] = cls_metadata['regexp'].pattern
                        module_metadata.append({
                            'class_name': name,
                            'metadata': obj.METADATA.__dict__
                        })

                # Append the module's metadata to the overall list
                if module_metadata:
                    modules_count += 1
                    classes_count += len(module_metadata)
                    country_code = str(module_name).split('.')[0]
                    if country_code not in country_codes:
                        country_codes.append(country_code)
                    metadata.append({
                        'package_name': package_name + '.' + module_name,
                        'country_code': country_code,
                        'ids': module_metadata
                    })

    print('----------------------------------------------------------------------------')
    print(f'Modules: {modules_count}')
    print(f'Countries: {len(country_codes)}')
    print(f'IDs: {classes_count}')
    print('----------------------------------------------------------------------------')
    # Write the metadata to a JSON file
    with open(output_filename, 'w') as f:
        json.dump(metadata, f, indent=2)


if __name__ == '__main__':
    collect_ids('idnumbers.nationalid', 'result.json')
