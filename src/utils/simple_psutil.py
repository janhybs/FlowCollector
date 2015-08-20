# encoding: utf-8
# author:   Jan Hybs

from subprocess import check_output
from utils.strings import extract_number


def cpu_count(logical=True):
    return int(
        check_output('nproc', shell=True).strip()
    )


def virtual_memory():
    memory_info = check_output('cat /proc/meminfo', shell=True).strip()
    return {
        'available': extract_number(memory_info, 'MemFree'),
        'total': extract_number(memory_info, 'MemTotal'),
    }