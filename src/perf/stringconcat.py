# encoding: utf-8
# author:   Jan Hybs
from perf.abstract import AbstractProcess


class StringConcat(AbstractProcess):
    """
    Test determining MEMORY performance
    Test complexity is constant
    """

    def test(self, result):
        i = 0
        a = 'a'
        score = 0
        while not self.exit.is_set():
            a += 'a'
            score = i
            i += 1
        result.value = score