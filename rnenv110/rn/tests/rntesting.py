
import unittest
from random import randint
from numpy import array, nditer, int_
from numpy import array_equal
from ..rn import RN
from ..rnreduce import __reduce_integer_unit as riu


class RNTest(unittest.TestCase):
    def test_validation(self):
        # test validation
        # try to initialize some randomly generated RN arrays
        real_numbers = [array([[[randint(-20, 20) for _ in range(3)]
                                for _ in range(3)] for _ in range(2)]) for _ in range(1000)]

        initialized = []
        for rn in real_numbers:
            try:
                initialized.append(RN(rn, randint(-10, 10)))
            except ValueError:
                continue
            except ZeroDivisionError:
                continue
        print(len(initialized))
        for rn in initialized:
            # validate
            self.assertEqual(len(rn.array.shape), 3)
            self.assertEqual(rn.array.shape[0], 2)
            self.assertEqual(rn.array.shape[2], 3)
            for item in rn.array.flat:
                self.assertEqual(isinstance(item, int) or isinstance(item, RN) or isinstance(item, int_), True)
            self.assertEqual(((rn.den[0, 0] == 0 or rn.den[0, 1] == 0) and len(rn.den) == 1), False)
            self.assertEqual((isinstance(rn.index, int) or isinstance(rn.index, RN)), True)

    def test_reduction(self):
        # TODO set up RN initialization masks to make unit testing possible
        pass


if __name__ == '__main__':
    unittest.main()
