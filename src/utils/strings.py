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