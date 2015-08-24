# encoding: utf-8
# author:   Jan Hybs
from perf._abstract import AbstractProcess


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