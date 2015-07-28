# encoding: utf-8
# author:   Jan Hybs
import filecmp
import json
from optparse import OptionParser
import os
from mysqldb import mysql_exec
from mongodb import mongo_exec

from utils.decoder import ProfilerJSONDecoder


# parse arguments
def create_parser():
    """Creates command line parse"""
    parser = OptionParser(usage="%prog [options] [file1 file2 ... filen]", version="%prog 1.0",
                          epilog="If no files are specified all json files in current directory will be selected. \n" +
                                 "Useful when there is not known precise file name only location")

    parser.add_option("-d", "--directory", dest="dirs", default=["./"], action="append",
                      help="Directory to be searched", metavar="DIR")
    # /var/www/html/flow-collector-arts
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
    if False:
        whole_program = json_data['children'][0]
        condition_id = mysql_exec.create_conditions(json_data)
        mysql_exec.create_structure(whole_program, parent=None)
        mysql_exec.add_measurements(whole_program, condition_id)
    else:
        mongo_exec.add_measurements(json_data)





if __name__ == '__main__':
    parser = create_parser()
    (options, args) = parse_args(parser)

    # print read_file(options.files[0])

    json_files_tmp = list(os.path.realpath(f) for f in options.files)

    print "Fetching json files"
    # traverse root directory, and list directories as dirs and files as files
    for dir in options.dirs:
        for root, dirs, files in os.walk(dir):
            for file in files:
                # accept json file only (for now)
                if file.lower().endswith('.json'):
                    json_files_tmp.append(os.path.realpath(os.path.join(root, file)))

    print "Removing duplicates"
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
    print "  Removed {:d} duplicated json files ({:d}, {:d})".format(len(json_files_tmp) - len(json_files),
                                                                     len(json_files_tmp), len(json_files))

    print 'Processing files'
    current_index = 1
    for json_file in json_files:
        print "  Processing file {:d}/{:d} '{:s}'".format(current_index, len(json_files), json_file)
        process_file(json_file)
        current_index += 1

    print 'Commiting changes to DB'
    mysql_exec.mysql_commit()

    print 'closing connection to DB'
    mysql_exec.mysql_close()
