# encoding: utf-8
# author:   Jan Hybs
from perf.abstract import AbstractProcess


class MatrixSolve(AbstractProcess):
    """
    Test determining CPU and MEMORY performance
    Test complexity is constant
    """

    def test(self, result):
        import numpy

        rnd = numpy.random.RandomState(1234)
        i = 0
        score = 0
        while not self.exit.is_set():
            matrix = rnd.random_sample((100, 100))
            numpy.linalg.inv(matrix)
            score = i
            i += 1
        result.value = score