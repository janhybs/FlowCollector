# encoding: utf-8
# author:   Jan Hybs

import re


def extract_number(data, name):
    lines = data.strip().split('\n')
    for line in lines:
        if line.find(name) != -1:
            match = re.match(r'.*\D(\d+)\D*', line)
            if match:
                return float(match.group(1))


def human_readable(number, round_result=False):
    units = ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']

    value = number

    if value < 10:
        return str(round(value, 6))

    for unit in units:
        if value >= 1000:
            value /= 1000.0
        else:
            return "{:s} {:s}".format(str(int(round(value)) if round_result else round(value, 3)), unit)