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
commit_data = False
# commit_data = True
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


class Runner(object):
    def __init__(self, module, options=None, args=None):
        self.module = module
        self.options = options
        self.args = args

        self.json_files_distinct = []
        self.json_files_all = []
        self.json_files_broken = []

        self.json_data = []

    def get_json_files (self):
        return self.json_files_distinct if self.json_files_distinct else self.json_files_all

    def get_json_data (self):
        return self.json_data

    def read_file(self, file):
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

    def process_file(self, json_data):
        try:
            return self.module.process_file(json_data)
        except Exception as e:
            print e

    def read_files(self, json_files):
        self.json_data = list()
        self.json_files_broken = list()
        for json_file in json_files:
            json_data = self.read_file(json_file)
            if not json_data:
                self.json_files_broken.append(json_file)
                continue

            self.json_data.append(json_data)
        return (self.json_data, self.json_files_broken)

    def process_all_files(self, json_files):
        i = 1
        for json_data in json_files:
            with timer.measured("file {:>4d} / {:d}".format(i, len(json_files))):
                self.process_file(json_data)
            i += 1

    def remove_duplicates(self, json_files):
        self.json_files_distinct = list()
        for a in json_files:
            match = False
            for b in self.json_files_distinct:
                # file do not have identical os.stat
                if filecmp.cmp(a, b, True):
                    match = True
                    break
            if not match:
                self.json_files_distinct.append(a)
        return self.json_files_distinct

    def fetch_files(self, options):
        self.json_files_all = list(os.path.realpath(f) for f in options.files)
        # traverse root directory, and list directories as dirs and files as files
        for dir in options.dirs:
            for root, dirs, files in os.walk(dir):
                for file in files:
                    # accept json file only (for now)
                    if file.lower().endswith('.json'):
                        self.json_files_all.append(os.path.realpath(os.path.join(root, file)))
        return self.json_files_all

    def run_benchmark(self, json_data):
        total = len(json_data)
        total = 150

        for i in range(2, total):
            with timer.measured("benchmark with {:03d} files".format(i)):
                for j in range(0, i):
                    self.module.process_file(json_data[j])

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


    with timer.measured('WHOLE PROCESS'):
        with timer.measured('open connection'):
            runner = Runner(ModCls(), options, args)

        with timer.measured('fetching files'):
            runner.fetch_files(options)

        with timer.measured('removing duplicates'):
            runner.remove_duplicates(runner.get_json_files())
            dupes = len(runner.json_files_all) - len(runner.json_files_distinct)

        with timer.measured('loading json files'):
            runner.read_files(runner.get_json_files())

        # with timer.measured('processing all files'):
        #     runner.process_all_files(runner.get_json_data())

        with timer.measured('committing changes'):
            if commit_data:
                runner.module.commit()

        with timer.measured('closing connection'):
            runner.module.close()

        print ''
        print ":: removed {:d} duplicates (total {:d}, distinct {:d})".format(dupes, len(runner.json_files_all), len(runner.json_files_distinct))
        print ":: {:d} broken files from total of {:d}".format(len(runner.json_files_broken), len(runner.json_files_distinct))
