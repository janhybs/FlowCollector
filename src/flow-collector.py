# encoding: utf-8
# author:   Jan Hybs
import filecmp
import json
from optparse import OptionParser
import os
import sys
from mongodb.mongo_exec import MongoExec

from utils.decoder import ProfilerJSONDecoder
import time

def_dir = '/var/www/html/flow-collector-arts/2015-07-28_11-12-25/tests/02_transport_12d'
# def_dir = '/var/www/html/flow-collector-arts/'
# commit_data = False
commit_data = True
# ModCls = MySQLExec
ModCls = MongoExec


class Timer(object):
    def __init__(self):
        self.times = { }
        self.names = { }
        self.level = 0

    def __enter__(self):
        self.times[self.level] = time.time()
        self.level += 1
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.level -= 1
        self.times[self.level] = time.time() - self.times[self.level]

        print "{:s} {:s}".format(Timer.format_name(self.names[self.level], self.level),
                                 Timer.format_time(self.times[self.level]))
        return self

    def time(self):
        return self.times[self.level]

    def measured(self, name):
        self.names[self.level] = name
        return self

    @staticmethod
    def format_name(name, level):
        return "{:80s}".format(level * '  ' + name)

    @staticmethod
    def format_time(value):
        n = "{:3.3f} ms".format(value * 1000)
        return "{0: >15}".format(n)


    @staticmethod
    def measure(method):
        def timed(*args, **kw):
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()
            # print '%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te-ts)
            print '{:80s} {:s}'.format(method.__name__, Timer.format_time(te - ts))
            return result

        return timed


timer = Timer()

# parse arguments
def create_parser():
    """Creates command line parse"""
    parser = OptionParser(usage="%prog [options] [file1 file2 ... filen]", version="%prog 1.0",
                          epilog="If no files are specified all json files in current directory will be selected. \n" +
                                 "Useful when there is not known precise file name only location")

    parser.add_option("-d", "--directory", dest="dirs", default=[def_dir], action="append",
                      help="Directory to be searched", metavar="DIR")
    #
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
            # print "error in file '{:s}'".format(e, file)
            return None


def process_file(module, json_data):
    try:
        module.process_file(json_data)
    except Exception as e:
        print e


def read_files(json_files):
    json_list = list()
    broken_list = list()
    for json_file in json_files:
        json_data = read_file(json_file)
        if not json_data:
            broken_list.append(json_file)
            continue

        json_list.append(json_data)
    return (json_list, broken_list)


def process_all_files(module, json_list):
    i = 1
    for json_data in json_list:
        with timer.measured("file {:>4d} / {:d}".format(i, len(json_list))):
            process_file(module, json_data)
        i += 1


def remove_duplicates(json_files_tmp):
    json_files = list()
    for a in json_files_tmp:
        match = False
        for b in json_files:
            # file do not have identical os.stat
            if filecmp.cmp(a, b, True):
                match = True
                break
        if not match:
            json_files.append(a)
    return json_files


def fetch_files(options):
    json_files_tmp = list(os.path.realpath(f) for f in options.files)
    # traverse root directory, and list directories as dirs and files as files
    for dir in options.dirs:
        for root, dirs, files in os.walk(dir):
            for file in files:
                # accept json file only (for now)
                if file.lower().endswith('.json'):
                    json_files_tmp.append(os.path.realpath(os.path.join(root, file)))
    return json_files_tmp


def run_benchmark(json_list):
    total = len(json_list)
    total = 150

    for i in range(2, total):
        with timer.measured("benchmark with {:03d} files".format(i)):
            for j in range(0, i):
                module.process_file(json_list[j])

        avg = (timer.time() / i) * 1000
        print "{:3d}) {:1.6f}".format(i, avg)
        with open('benchmark.log', 'a+') as fp:
            fp.write("{:d},{:1.6f}\n".format(i, avg))


if __name__ == '__main__':
    parser = create_parser()
    (options, args) = parse_args(parser)

    mongo = MongoExec()
    # for item in mongo.cond.find({"run-process-count" : 1}): #
    # print item

    with timer.measured('fooooooooooo'):
        result = []
        for item in mongo.metrics.find({ 'ist_id': ',Whole Program,' }):
            if mongo.cond.find({ '_id': item['cond_id'], "run-process-count": 3 }).count():
                result.append(item)
        print len(result)

    with timer.measured('fooooooooooo'):
        result = []
        for item in mongo.metrics.find({ 'ist_id': ',Whole Program,' }):
            if mongo.cond.find_one({ '_id': item['cond_id'], "run-process-count": 3 }):
                result.append(item)
        print len(result)

    with timer.measured('ffffffffffffff'):
        result = []
        # all 'Whole Program's conditions ids
        try:
            conditions_ids = mongo.pluck_fields (
                collection=mongo.metrics,
                fields=["cond_id"],
                match={'ist_id': ',Whole Program,'},
                group='$ist_id'
            )['cond_id']

            metrics_id = mongo.pluck_fields (
                collection=mongo.cond,
                fields=['_id'],
                match={
                    '_id': { '$in': conditions_ids },
                    "run-process-count": 3
                    },
                group=''
            )['data']
            for item in mongo.metrics.find({ 'cond_id': { '$in': metrics_id }, 'ist_id': ',Whole Program,' }):
                result.append(item)
            print len(result)
        except Exception as e:
            print e

        sys.exit (0)
        """
        cond_ids1 = list(mongo.pluck_field(id=',Whole Program,', pluck_field='cond_id'))[0]['data']
        pipeline = [
            {
                '$match': {
                    '_id': { '$in': cond_ids1 },
                    "run-process-count": 3
                }
            },
            {
                '$group': {
                    '_id': '',
                    'data': { '$push': "$_id" }
                }
            }
        ]
        cond_ids2 = list(mongo.cond.aggregate(pipeline))[0]['data']
        for item in mongo.metrics.find({ 'cond_id': { '$in': cond_ids2 }, 'ist_id': ',Whole Program,' }):
            result.append(item)
        print len(result)
        """
    sys.exit(0)

    with timer.measured('WHOLE PROCESS'):
        with timer.measured('open connection'):
            module = ModCls()

        with timer.measured('fetching files'):
            json_files_tmp = fetch_files(options)

        with timer.measured('removing duplicates'):
            json_files = remove_duplicates(json_files_tmp)
            dupes = len(json_files_tmp) - len(json_files)

        with timer.measured('loading json files'):
            (json_list, broken_list) = read_files(json_files)

        with timer.measured('processing all files'):
            process_all_files(module, json_list)
        # run_benchmark(json_list)

        with timer.measured('committing changes'):
            if commit_data:
                module.commit()
            pass

        with timer.measured('closing connection'):
            module.close()

        print ''
        print ":: removed {:d} duplicates ({:d}, {:d})".format(dupes, len(json_files_tmp), len(json_files))
        print ":: {:d} broken files from total of {:d}".format(len(broken_list), len(json_files))
