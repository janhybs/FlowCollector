# encoding: utf-8
# author:   Jan Hybs
from perf._abstract import AbstractProcess


class ForLoop(AbstractProcess):
    def test(self, result):
        i = 0
        score = 0
        while not self.exit.is_set():
            score += i
            i += 1
        result.value = score