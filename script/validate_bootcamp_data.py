"""Ensure proper YAML and required fields/types are present."""
import argparse
import os
import sys

import yaml
from logger import logger


BOOTCAMP_REQUIRED_KEYS = {
    'description': {str, unicode},
    'display_name': {str},
    'founded_year': {int},
    'primary_email': {str},
    'programs': {dict},
    'website': {str},
}


PROGRAM_REQUIRED_KEYS = {
    'admissions': {str},
    'cities': {list},
    'commitment': {str},
    'cost_description': {str, unicode},
    'description': {str, unicode},
    'display_name': {str},
    'duration': {int, str},
    'duration_units': {str},
    'financing': {bool},
    'guarantee': {str, unicode},
    'outcomes_verified': {bool},
    'placement': {bool, str},
    'reports_outcomes': {bool},
    'scholarships': {bool, str},
    'topics': {list},
}


def main(directory):
    errors = []
    error_msg = '[{}]'.format(directory)

    # Verify folder name is lower cased
    if directory.lower() != directory:
        errors.append('{} slug must be lowercased.'.format(directory))

    # Verify a logo.png exists within the directory
    if not os.path.isfile('{}logo.png'.format(directory)):
        errors.append('{} Missing logo.png'.format(error_msg))

    # Verify data.yml exists within the directory
    if not os.path.isfile('{}data.yml'.format(directory)):
        errors.append('{} Missing data.yml'.format(error_msg))
        # No point in going any further, return
        return errors

    all_cities = [
        city.get('slug') for city in yaml.load(open('cities.yml', 'r'))]
    all_topics = [
        topic.get('slug') for topic in yaml.load(open('topics.yml', 'r'))]
    all_cities_topics = all_cities + all_topics

    # Validate bootcamp yaml data
    data = yaml.load(open('{}data.yml'.format(directory), 'r'))

    missing_keys_bootcamp = set.difference(
        set(BOOTCAMP_REQUIRED_KEYS), set(data))

    if missing_keys_bootcamp:
        errors.append(
            '{} Missing required keys in data.yml: {}'.format(
                error_msg, missing_keys_bootcamp))

    for key, req_types in BOOTCAMP_REQUIRED_KEYS.items():
        key_type = type(data.get(key))
        if (
                key not in missing_keys_bootcamp and
                key_type not in req_types):
            errors.append(
                '{} Incorrect format for key "{}". Should be {} but was a '
                '{}'.format(error_msg, key, req_types, key_type))

    if not data.get('programs'):
        errors.append(
            '{} At least one program required per bootcamp.'.format(error_msg))
        # No point going any further, return
        return errors

    for program_slug, program_data in data.get('programs').items():
        error_msg = '[{}{}]'.format(directory, program_slug)
        missing_keys_program = set.difference(
            set(PROGRAM_REQUIRED_KEYS), set(program_data))
        if missing_keys_program:
            errors.append(
                '{} Missing required keys: {}'.format(
                    error_msg, missing_keys_program))
        for key, req_types in PROGRAM_REQUIRED_KEYS.items():
            key_type = type(program_data.get(key))
            if (
                    key not in missing_keys_program and
                    key_type not in req_types):
                errors.append(
                    '{} Incorrect format for key "{}". Should be {} but was '
                    'a {}'.format(error_msg, key, req_types, key_type))
        # City and topic slugs must be lower case
        cities_topics = program_data.get('cities') + program_data.get('topics')
        for ct in cities_topics:
            if ct.lower() != ct:
                errors.append(
                    '{} City/Topic slug {} must be lower cased.'.format(
                        error_msg, ct))
            elif ct not in all_cities_topics:
                errors.append(
                    '{} City/Topic {} not found in data. '
                    'Please add it to the correct yml file.'.format(
                        error_msg, ct))

    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse files to be checked')
    parser.add_argument(
        '--directory', help='The bootcamp directory to be validated')
    args = parser.parse_args()
    directory = args.directory

    errors = main(args.directory)
    if errors:
        logger.error('\n{}\n'.format('\n'.join(errors)))
        sys.exit(1)

    sys.exit(0)
