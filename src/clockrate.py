# encoding: utf-8
# author:   Jan Hybs

from multiprocessing import Process, Value, Event
from optparse import OptionParser
import time
import hashlib
import re
import json
import platform
from subprocess import check_output

try:
    import psutil
except ImportError as e:
    import utils.psutil as psutil

try:
    from pluck import pluck
except ImportError as e:
    from utils.pluck import pluck

from utils.timer import Timer
from utils.progressbar import ProgressBar


timer = Timer()


class AbstractProcess(Process):
    def __init__(self, ):
        Process.__init__(self)
        self.exit = Event()
        self.result = Value('f', 0)
        self.terminated = None

    def run(self):
        self.test(self.result)

    def shutdown(self):
        if self.is_alive():
            self.exit.set()
            self.terminated = True
        else:
            self.terminated = False

    def test(self, result):
        pass


class ForLoop(AbstractProcess):
    def test(self, result):
        i = 0
        score = 0
        while not self.exit.is_set():
            score += i
            i += 1
        result.value = score


class Factorial(AbstractProcess):
    def test(self, result):
        import math

        i = 0
        score = 0
        while not self.exit.is_set():
            math.factorial(i)
            score += i
            i += 1
        result.value = score

    def factorial(self, n):
        # return math.factorial(n)
        return reduce(lambda x, y: x * y, [1] + range(1, n + 1))


class HashSHA(AbstractProcess):
    def test(self, result):
        i = 0
        score = 0
        while not self.exit.is_set():
            hashlib.sha512('1234').hexdigest()
            score += i
            i += 1
        result.value = score


class MatrixCreate(AbstractProcess):
    def test(self, result):
        import numpy

        rnd = numpy.random.RandomState(1234)
        i = 0
        score = 0
        while not self.exit.is_set():
            rnd.random_sample((i + 1, i + 1))
            score += i
            i += 1
        result.value = score


class MatrixSolve(AbstractProcess):
    def test(self, result):
        import numpy

        rnd = numpy.random.RandomState(1234)
        i = 0
        score = 0
        while not self.exit.is_set():
            matrix = rnd.random_sample((i + 1, i + 1))
            numpy.linalg.inv(matrix)
            score += i
            i += 1
        result.value = score


class StringConcat(AbstractProcess):
    def test(self, result):
        i = 0
        a = 'a'
        score = 0
        while not self.exit.is_set():
            a += i * 'a'
            score += i
            i += 1
        result.value = score


class BenchmarkMeasurement(object):
    def __init__(self):
        self.timeout = .5
        self.tries = 3
        self.processes = 1

    def measure(self, cls, name, timeout=None, tries=None, processes=None):
        timeout = timeout if timeout is not None else self.timeout
        tries = tries if tries is not None else self.tries
        processes = processes if processes is not None else self.processes

        pb = ProgressBar(maximum=tries, width=30, prefix="{self.name:25}",
                         suffix=" {self.last_progress}/{self.maximum}")

        measure_result = list()
        for no_cpu in processes:
            pb.name = "{:s} {:d} {:s}".format(name, no_cpu, 'core' if no_cpu == 1 else 'cores')
            results = list()
            for i in range(0, tries):
                if print_output:
                    pb.progress(i)

                targets = [cls() for j in range(0, no_cpu)]

                with timer.measured("{:s} {:d}".format(name, i), False):
                    # start processes
                    for target in targets:
                        target.start()

                    # wait for timeout
                    time.sleep(timeout)

                    # send exit status
                    for target in targets:
                        target.shutdown()

                    # join threads
                    for target in targets:
                        target.join()

                tmp = dict()
                tmp['duration'] = timer.time()
                tmp['value'] = sum(pluck(targets, 'result.value'))
                tmp['exit'] = not max(pluck(targets, 'terminated'))
                results.append(tmp)

            if print_output:
                pb.end()

            result = dict()
            result['exit'] = min(pluck(results, 'exit'))
            result['value'] = sum(pluck(results, 'value')) / float(tries)
            result['duration'] = sum(pluck(results, 'duration')) / float(tries)
            result['performance'] = result['value'] / result['duration']
            result['processes'] = no_cpu

            measure_result.append(result)

        return measure_result


    def configure(self, timeout, tries, processes):
        self.timeout = timeout
        self.tries = tries
        self.processes = processes if type(processes) is list else [processes]


print_output = True
all_tests = set(['for-loop', 'factorial', 'hash-sha', 'matrix-creation', 'matrix-solve', 'string-concat'])


def create_parser():
    """Creates command line parse"""
    parser = OptionParser()

    parser.add_option("-i", "--include", dest="includes", metavar="TESTNAME", default=[], action="append",
                      help="Turn on specific tests, by default all tests are included")
    parser.add_option("-x", "--exclude", dest="excludes", metavar="TESTNAME", default=[], action="append",
                      help="Turn off specific tests")
    parser.add_option("-c", "--core", dest="cores", metavar="CORE", default=[], action="append",
                      help="Try test with this amount of core, by default 1...N, where N is maximum cores available")

    parser.add_option("-d", "--duration", dest="timeout", metavar="DURATION", default=0.4,
                      help="Maximum duration per one test case")
    parser.add_option("-t", "--tries", dest="tries", metavar="TRIES", default=2,
                      help="Number of tries for each test")
    parser.add_option("-q", "--quiet", dest="quiet", default=True, action="store_false",
                      help="Do not print any output")

    parser.set_usage("""%prog [options]""")
    return parser


def parse_args(parser):
    global print_output

    """Parses argument using given parses and check resulting value combination"""
    (options, args) = parser.parse_args()

    includes = set(options.includes) if options.includes else all_tests.copy()
    if options.excludes:
        includes = includes - set(options.excludes)

    if not options.cores:
        options.cores = range(1, psutil.cpu_count(logical=True) + 1)
    else:
        options.cores = [int(value) for value in options.cores]

    options.tries = int(options.tries)
    options.timeout = float(options.timeout)
    print_output = options.quiet

    assert options.tries > 0, 'Number of tries must be positive integer'
    assert options.timeout > 0, 'Timeout value must be positive number'

    return options, args, includes


def main():
    parser = create_parser()
    (options, args, includes) = parse_args(parser)

    try:
        with timer.measured('node-performance', print_output):
            if print_output:
                print "{:-^55}".format("Running tests")
                print "{:-^55}".format(str(includes))

            measurement = BenchmarkMeasurement()
            measurement.configure(options.timeout, options.tries, options.cores)

            test_results = dict()
            if 'for-loop' in includes:
                test_results['for-loop'] = measurement.measure(ForLoop, 'For loop')

            if 'factorial' in includes:
                test_results['factorial'] = measurement.measure(Factorial, 'Factorial')

            if 'hash-sha' in includes:
                test_results['hash-sha'] = measurement.measure(HashSHA, 'Hash')

            if 'matrix-creation' in includes:
                test_results['matrix-creation'] = measurement.measure(MatrixCreate, 'Matrix create')

            if 'matrix-solve' in includes:
                test_results['matrix-solve'] = measurement.measure(MatrixSolve, 'Matrix solve')

            if 'string-concat' in includes:
                test_results['string-concat'] = measurement.measure(StringConcat, 'String concat')

            if print_output:
                print "\n{:-^55}".format("Getting node info")

            info = dict()
            info['memory'] = dict()
            info['memory']['total'] = psutil.virtual_memory().total
            info['memory']['avail'] = psutil.virtual_memory().available

            # info['disk'] = [psutil.disk_partitions()]
            info['cpu'] = dict()
            info['cpu']['physical'] = psutil.cpu_count(logical=False)
            info['cpu']['logical'] = psutil.cpu_count(logical=True)
            info['cpu']['architecture'] = platform.processor()
            if platform.system() == 'Linux':
                cpu_info = check_output('cat /proc/cpuinfo', shell=True).split('\n')
                for line in cpu_info:
                    if "model name" in line:
                        info['cpu']['name'] = re.sub(".*model name.*:", "", line, 1).strip()
                    if "cpu MHz" in line:
                        info['cpu']['frequency'] = float(re.sub(".*cpu MHz.*:", "", line, 1).strip())


            elif platform.system() == 'Windows':
                cpu_freq = check_output('wmic cpu get MaxClockSpeed', shell=True)
                cpu_freq = cpu_freq.replace('\n', '').replace('MaxClockSpeed', '').strip()
                info['cpu']['frequency'] = int(cpu_freq)

                cpu_name = check_output('wmic cpu get Caption', shell=True)
                cpu_name = cpu_name.replace('\n', '').replace('Caption', '').strip()
                info['cpu']['name'] = cpu_name

            info['system'] = dict()
            info['system']['platform'] = platform.system()
            info['system']['processor'] = platform.processor()
            info['system']['version'] = platform.version()
            info['system']['machine'] = platform.machine()
            info['system']['node'] = platform.node()
            info['system']['release'] = platform.release()

            clockrate_result = { 'architecture': info, 'tests': test_results }

            with open('node_test.json', 'w') as fp:
                json.dump(clockrate_result, fp, indent=4, sort_keys=True)

            if print_output:
                with open('node_test.json', 'r') as fp:
                    print fp.read()
    except Exception as e:
        print e
        raise e


if __name__ == '__main__':
    main()