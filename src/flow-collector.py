# encoding: utf-8
# author:   Jan Hybs
import filecmp

import json, mysql.connector
from optparse import OptionParser
import os
from config import credentials

from utils.decoder import ProfilerJSONDecoder
from utils.dotdict import DotDict
from utils.sql import insert_condition_query, insert_condition_fields, insert_structure_query, insert_measurement_query

connector = mysql.connector.connect(**credentials)
cursor = connector.cursor()


def create_conditions(json_data):
    data = { key: json_data[key] for key in insert_condition_fields }
    cursor.execute(insert_condition_query, data)

    return cursor.lastrowid


def create_structure(json_data, parent=None):
    try:
        cursor.execute(insert_structure_query, { 'name': json_data['tag'], 'parent': parent })
    except mysql.connector.errors.IntegrityError as e:
        # print e
        pass

    if 'children' in json_data:
        for child in json_data['children']:
            create_structure(child, json_data['tag'])


def create_measurement(json_data, field, condition_id):
    return {
        'type': field,
        'value': json_data[field],
        'structure': json_data['tag'],
        'cond': condition_id
    }


def add_measurements(json_data, condition_id):
    # store all keys
    fields = json_data.keys()

    # except children
    if 'children' in fields:
        fields.remove ('children')

    for field in fields:
        data = create_measurement(json_data, field, condition_id)
        cursor.execute(insert_measurement_query, data)

    if 'children' in json_data:
        for child in json_data['children']:
            add_measurements(child, condition_id)


# parse arguments
def create_parser():
    """Creates command line parse"""
    parser = OptionParser(usage="%prog [options] [file1 file2 ... filen]", version="%prog 1.0",
                          epilog="If no files are specified all json files in current directory will be selected. \n" +
                                 "Useful when there is not known precise file name only location")

    parser.add_option("-d", "--directory", dest="dirs", default=["./"], action="append",
                      help="Directory to be searched", metavar="DIR")
    parser.add_option("-f", "--file", dest="files", default=['../data/example.json'], action="append",
                      help="Directory to be searched", metavar="FILE")
    parser.add_option("-n", "--non-recursive", dest="non_recursive", default=False, action='store_true',
                      help="Disallow recursive search", metavar="")
    return parser


def parse_args(parser):
    """Parses argument using given parses and check resulting value combination"""
    (options, args) = parser.parse_args()

    # for now, no check needed

    return (options, args)


def read_file(file):
    if not os.path.exists(file):
        print "No such file {:s}'".format(file)
        return None

    with open(file, 'r') as fp:
        raw_data = fp.read()
        try:
            json_data = json.loads(raw_data, encoding="utf-8", cls=ProfilerJSONDecoder)
            if 'program-name' not in json_data or json_data['program-name'] != 'Flow123d':
                raise Exception('Unsupported json structure')

            return json_data
        except Exception as e:
            print "{:s}: file '{:s}'".format(e, file)
            return None


def process_file(file):
    json_data = read_file(file)
    if not json_data:
        return

    condition_id = create_conditions(json_data)
    whole_program = json_data['children'][0]
    create_structure(whole_program, parent=None)
    add_measurements(whole_program, condition_id)


if __name__ == '__main__':
    parser = create_parser()
    (options, args) = parse_args(parser)

    # print read_file(options.files[0])

    json_files_tmp = list(os.path.realpath(f) for f in options.files)

    # traverse root directory, and list directories as dirs and files as files
    for dir in options.dirs:
        for root, dirs, files in os.walk(dir):
            for file in files:
                # accept json file only (for now)
                if file.lower().endswith('.json'):
                    json_files_tmp.append(os.path.realpath(os.path.join(root, file)))

    json_files = list()
    for a in json_files_tmp:
        match = False
        for b in json_files:
            # file do not have identical os.stat
            if filecmp.cmp(a, b, True):
                # print '{:s} is same as {:s}'.format(os.path.realpath(a), os.path.realpath(b))
                match = True
                break
        if not match:
            json_files.append(a)

    print "Removed {:d} duplicated json files ({:d}, {:d})".format(len(json_files_tmp) - len(json_files), len(json_files_tmp), len(json_files))

    for json_file in json_files:
        print "Processing file '{:s}'".format(json_file)
        process_file(json_file)


    print 'done'
    print 'commiting'
    connector.commit()

    print 'closing connection to DB'
    cursor.close()
    connector.close()
    