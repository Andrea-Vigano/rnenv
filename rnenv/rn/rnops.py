"""
file to store all the methods and functions related to the operations between RNs
following the matrix_rn_representation protocol for ops
"""

from numpy import ndarray, zeros, lcm
from itertools import product


def linears_product(a: ndarray, b: ndarray) -> ndarray:
    """
    returns the product (as matrix) of the two linears a and b

    follows the matrix_rn_representation protocol:

    LINEARS MULTIPLICATION:
        multiplication between num or den matrices

        (4 + 2√2) * (5 - 6√3) = 20 - 24√3 + 10√2 - 12√6

        |4  1  1|   |5  1  1|   |a[0] * b[0] ->  20  1   1|
        |2  2  2| * |-6 3  2| = |a[0] * b[1] -> -24  3   2|
                                |a[1] * b[0] ->  10  2   2|
                                |a[1] * b[1] -> -12  6   2|

        combine units of the two factors:
            will call them a and b
            -> if one of the 1-2 is 1, 1:
                pure product
            -> else:
                get indexes lcm
                (using numpy.lcm)
                coefficient product, M ** (lcm // index) * other..., indexes lcm

    :param a: linear number matrix
    :param b: linear number matrix
    :return: product of a and b linears (matrix)
    """

    # product algorithm
    # will assume that the linears have already been reduced
    result = zeros((a.shape[0] * b.shape[0], 3), dtype=int)

    # combination of a units and b units
    for i, pair in enumerate(product(a, b)):
        if any(True for unit in pair if (unit == 1)[1:3].all()):
            # simple product
            result[i] = pair[0] * pair[1]
        else:
            # complex product
            one = pair[0]
            two = pair[1]
            _lcm = lcm(one[2], two[2])
            result[i] = [one[0] * two[0],
                         (one[1] ** (_lcm // one[2])) * (two[1] ** (_lcm // two[2])),
                         _lcm]
    return result


if __name__ == '__main__':
    # some fast testing
    from numpy import array
    from random import randint
    from rnenv.rn.rnreduce import __reduce_linear

    _one = array([[4, 1, 1], [2, 2, 2]])
    _two = array([[5, 1, 1], [-6, 3, 2]])

    print(linears_product(_one, _two))

    data = [__reduce_linear(
        array([array([randint(-10, 10), randint(1, 5), randint(1, 3)]) for _ in range(randint(1, 4))]))
            for _ in range(1000)]

    for i in range(0, len(data), 2):
        print('Starting linear:\n {}\n\n{}'.format(data[i], data[i + 1]))
        print('Parsed data:\n {}\n'.format(linears_product(data[i], data[i + 1])))
