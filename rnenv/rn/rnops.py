"""
file to store all the methods and functions related to the operations between RNs
following the matrix_rn_representation protocol for ops
"""

from numpy import array

from rnenv.rn.linearsops import linears_product, linears_sum
from rnenv.rn.rnreduce import fill_size_difference


def rn_neg(a):
    """
    change sign of numerator

    :param a: RN object (access array with a.array)
    :return: -a array
    """

    # copy a to not modify original array data
    ar = a.array
    ar[0, :, 0] = -ar[0, :, 0]
    return ar


def rn_abs(a):
    """
    change signs of a if a < 0

    :param a: RN object
    :return: |a|
    """

    return a if a > 0 else -a


# operation decorator
def validate(op):
    def wrapper(self, other):
        # validate other
        if not any(isinstance(other, tp) for tp in self.COMPATIBLE_TYPES + (type(self), )):
            raise ValueError('Bad user argument, cannot perform {} for {} object {} with {} object {},'
                             'must be {}'.format(
                              str(op), type(self), str(self), type(other), str(other),
                              self.COMPATIBLE_TYPES + (type(self), )))
        rv = op(self, other)
        return array([*fill_size_difference(rv[0], rv[1])])
    return wrapper


@validate
def rn_add(a, b):
    """
    a + b
    return a.num * b.den + b.num * a.den / a.den * b.den

    using linears_product and linears_sum

    :param a: RN object
    :param b: RN object
    :return: sum array
    """

    return array([linears_sum(linears_product(a.num, b.den), linears_product(b.num, a.den)),
                  linears_product(a.den, b.den)])


def rn_sub(a, b):
    """
    a - b
    uses rn_sum and rn_neg to get the difference like a + (-b)

    :param a: RN object
    :param b: RN object
    :return:  difference array
    """

    return a + (-b)


@validate
def rn_mul(a, b):
    """
    a * b
    build product like a.num * b.num / a.den * b.den

    :param a: RN object
    :param b: RN object
    :return: product array
    """

    return array([linears_product(a.num, b.num), linears_product(a.den, b.den)])


@validate
def rn_div(a, b):
    """
    a / b
    build quotient like a.num * b.den / a.den * b.num

    :param a: RN object
    :param b: RN object != 0
    :return: quotient array
    """

    if b == 0:
        raise ValueError('Bad user argument, cannot divide {} by zero'.format(a))
    return array([linears_product(a.num, b.den), linears_product(a.den, b.num)])


if __name__ == '__main__':
    # some fast testing
    from random import randint
    from rnenv.rn.rnreduce import __reduce_linear

    _one = array([[4, 1, 1], [2, 2, 2]])
    _two = array([[5, 1, 1], [-6, 3, 2]])

    print(linears_product(_one, _two))

    data = [__reduce_linear(
        array([array([randint(-10, 10), randint(1, 5), randint(1, 3)]) for _ in range(randint(1, 4))]))
            for _ in range(1000)]

    for _i in range(0, len(data), 2):
        print('Starting linear:\n {}\n\n{}'.format(data[_i], data[_i + 1]))
        print('Parsed data:\n {}\n'.format(linears_product(data[_i], data[_i + 1])))
