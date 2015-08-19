# encoding: utf-8
# author:   Jan Hybs

from multiprocessing import Process, Value, Event
import time
import math
import hashlib
import numpy
import re
import json
import platform
from subprocess import check_output

import psutil
from pluck import pluck

from utils.timer import Timer
from utils.progressbar import ProgressBar


timer = Timer()


class AbstractProcess(Process):
    def __init__(self, ):
        Process.__init__(self)
        self.exit = Event()
        self.result = Value('i', 0)
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
        while not self.exit.is_set():
            result.value = i
            i += 1


class Factorial(AbstractProcess):
    def test(self, result):
        i = 0
        while not self.exit.is_set():
            result.value = i
            math.factorial(i)
            i += 1

    def factorial(self, n):
        # return math.factorial(n)
        return reduce(lambda x, y: x * y, [1] + range(1, n + 1))


class HashSHA(AbstractProcess):
    def test(self, result):
        i = 0
        while not self.exit.is_set():
            result.value = i
            hashlib.sha512('1234').hexdigest()
            i += 1


class MatrixCreate(AbstractProcess):
    def test(self, result):
        rnd = numpy.random.RandomState(1234)
        i = 0
        while not self.exit.is_set():
            matrix = rnd.random_sample((i + 1, i + 1))
            result.value = i
            i += 1


class MatrixSolve(AbstractProcess):
    def test(self, result):
        rnd = numpy.random.RandomState(1234)
        i = 0
        while not self.exit.is_set():
            matrix = rnd.random_sample((i + 1, i + 1))
            result.value = i
            numpy.linalg.inv(matrix)
            i += 1



class StringConcat(AbstractProcess):
    def test(self, result):
        i = 0
        a = 'a'
        while not self.exit.is_set():
            a += i * 'a'
            result.value = i
            i += 1


class BenchmarkMeasurement(object):
    def __init__(self):
        pass

    def run(self, target, timeout, name="method name"):
        result = { 'value': None, 'exit': None, 'value': None }

        with timer.measured(name, False):
            target.start()
            time.sleep(timeout)
            target.shutdown()

        result['duration'] = timer.time()
        result['value'] = target.result.value
        result['exit'] = not target.terminated

        return result

    def measure(self, cls, name, timeout, tries=5):
        pb = ProgressBar(maximum=tries, width=30, prefix="{self.name:20}", suffix=" {self.last_progress}/{self.maximum}")
        pb.name = name

        results = list()
        for i in range(0, tries):
            if print_output:
                pb.progress(i)
            tmp = measurement.run(cls(), name=name + str(i + 1), timeout=timeout)
            results.append(tmp)

        if print_output:
            pb.end()

        result = dict()
        result['exit'] = min(pluck(results, 'exit'))
        result['value'] = sum(pluck(results, 'value')) / float(tries)
        result['duration'] = sum(pluck(results, 'duration')) / float(tries)
        result['performance'] = result['value'] / result['duration']

        return result
        # print tests



# import os, platform, subprocess, re
#
# def get_processor_name():
# if platform.system() == "Windows":
# return platform.processor()
#     elif platform.system() == "Darwin":
#         import os
#         os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
#         command ="sysctl -n machdep.cpu.brand_string"
#         return subprocess.check_output(command).strip()
#     elif platform.system() == "Linux":
#         command = "cat /proc/cpuinfo"
#         all_info = subprocess.check_output(command, shell=True).strip()
#         for line in all_info.split("\n"):
#             if "model name" in line:
#                 return re.sub( ".*model name.*:", "", line,1)
#     return ""
#
# print get_processor_name()

# print info
# print tests
print_output = True
measure_time = 0.3

if __name__ == '__main__':
    try:
        with timer.measured('node-performance'):
            if print_output:
                print "{:-^55}".format("Running tests")

            measurement = BenchmarkMeasurement()

            tests = dict()
            tests['for-loop'] = measurement.measure(ForLoop, 'For loop ', measure_time)
            tests['factorial'] = measurement.measure(Factorial, 'Factorial ', measure_time)
            tests['hash-sha'] = measurement.measure(HashSHA, 'Hash ', measure_time)
            tests['matrix-creation'] = measurement.measure(MatrixCreate, 'Matrix create ', measure_time)
            tests['matrix-solve'] = measurement.measure(MatrixSolve, 'Matrix solve ', measure_time)
            tests['string-concat'] = measurement.measure(StringConcat, 'String concat ', measure_time)

            if print_output:
                print "\n{:-^55}".format("Getting node info")

            info = dict()
            info['memory'] = dict()
            info['memory']['total'] = psutil.virtual_memory().total
            info['memory']['avail'] = psutil.virtual_memory().available

            # info['disk'] = [psutil.disk_partitions()]
            info['cpu'] = dict()
            info['cpu']['physical'] = psutil.cpu_count(logical=False)
            info['cpu']['logical']  = psutil.cpu_count(logical=True)
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
                cpu_freq = cpu_freq.replace('\n', '').replace ('MaxClockSpeed', '').strip()
                info['cpu']['frequency'] = int(cpu_freq)

                cpu_name = check_output('wmic cpu get Caption', shell=True)
                cpu_name = cpu_name.replace('\n', '').replace ('Caption', '').strip()
                info['cpu']['name'] = cpu_name

            clockrate_result = { 'architecture': info, 'tests': tests }

            with open('node_test.json', 'w') as fp:
                json.dump(clockrate_result, fp, indent=4 )

            if print_output:
                with open('node_test.json', 'r') as fp:
                    print fp.read()
    except Exception as e:
        print e
        raise e



