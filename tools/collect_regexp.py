import json
import argparse


def collect_regexp(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    new_data = {}
    for item in data:
        country_code = item['country_code']
        if len(country_code) != 3:
            continue
        if country_code in new_data:
            regexps = new_data[country_code]
        else:
            regexps = {}
            new_data[country_code] = regexps
        for identity in item['ids']:
            class_name = identity['class_name']
            metadata = identity['metadata']
            regexps[class_name] = metadata['regexp']

    with open(output_file, 'w') as f:
        json.dump(new_data, f, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='path to the input JSON file')
    parser.add_argument('output_file', help='path to the output JSON file')
    args = parser.parse_args()
    collect_regexp(args.input_file, args.output_file)
