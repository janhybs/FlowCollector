# encoding: utf-8
# author:   Jan Hybs
from perf.abstract import AbstractProcess


class ForLoop(AbstractProcess):
    """
    Test determining CPU performance
    Test complexity is constant
    """

    def test(self, result):
        i = 0
        score = 0
        while not self.exit.is_set():
            score = i
            i += 1
        result.value = score