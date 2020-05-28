"""
file to store all the function for linears objects (matrices) operations
"""

from numpy import ndarray, zeros, vstack, copy, lcm
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


def linears_sum(a: ndarray, b: ndarray):
    """
    returns the sum of the linear numbers a and b, represented by two matrices
    following the matrix_rn_reduction protocol:

    LINEARS SUM:

        when a real number is instantiated, it is automatically reduced, so we can just concatenate
        the two terms and the reducer will do their job

    :param a: linear number matrix
    :param b: linear number matrix
    :return: sum of a and b
    """

    # sum algorithm
    # will assume that the linears have already been reduced
    return vstack((a, b))


def linear_conjugate(a: ndarray):
    """
    returns the conjugate of a
    len(a) must be 2.
    Linear conjugate: 1 + √2 -> 1 - √2
    Won't validate parameters because this function should only be called by
    other methods and not by the user

    Following matrix_rn_representation protocol:

    LINEAR CONJUGATE: a
        get the conjugate of a len = 2 linear object
        when a linear has been reduced, integers units should
        come on the first row of the matrix

        return an array like [a[0], -a[1, 0] + a[1, 1:]]

    :param a: reduced linear object of len 2
    :return:
    """

    b = copy(a)
    b[1, 0] = -b[1, 0]
    return b
