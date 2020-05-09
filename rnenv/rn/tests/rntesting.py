
import unittest
from random import randint
from numpy import array as ar
from numpy import array_equal
from ..rnreduce import __reduce_integer_unit as riu


class RNTest(unittest.TestCase):
    def test_init(self):
        # test validation

        # test reduction
        # -> unit reduction
        unit_samples = [
            ar([3, 0, 0]),
            ar([-4, 0, 0]),
            ar([12, 0, 0]),
            ar([3, 5, 2]),
            ar([1, -6, -3]),
            ar([-7, 3, 2]),
            ar([0, 4, 2]),
            ar([0, -3, 7]),
            ar([0, 5, -3]),
            ar([5, 1, 5]),
            ar([-4, 1, -6]),
            ar([4, -1, 3]),
            ar([3, 4, 2]),
            ar([4, 8, 2]),
            ar([-12, 16, 4]),
            ar([6, -8, 3]),
            ar([1, 0, 2]),
            ar([10, 0, 15]),
            ar([4, 0, -9]),
            ar([5, 128, 6]),
            ar([1, 25, 2]),
            ar([6, 125, 3])
        ]
        samples_results = [
            ar([3, 0, 0]),
            ar([-4, 0, 0]),
            ar([12, 0, 0]),
            ar([3, 5, 2]),
            ar([1, -6, -3]),
            ar([-7, 3, 2]),
            ar([0, 0, 0]),
            ar([0, 0, 0]),
            ar([0, 0, 0]),
            ar([5, 0, 0]),
            ar([-4, 0, 0]),
            ar([-4, 0, 0]),
            ar([6, 0, 0]),
            ar([8, 2, 2]),
            ar([-24, 0, 0]),
            ar([-12, 0, 0]),
            ar([0, 0, 0]),
            ar([0, 0, 0]),
            ar([0, 0, 0]),
            ar([40, 2, 2]),
            ar([5, 0, 0]),
            ar([30, 0, 0])
        ]
        for sample, result in zip(unit_samples, samples_results):
            print(sample)
            print(riu(sample))
            print()
            self.assertTrue(array_equal(riu(sample), result))

        # test linear reduction


if __name__ == '__main__':
    unittest.main()
