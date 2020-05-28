"""
Functions storage
"""

from math import gcd


def reduce_fraction(num: int, den: int):
    """
    reduce fraction to prime terms

    :param num: numerator int
    :param den: denominator int
    :return: reduced num and den
    """
    _gcd = gcd(num, den)
    return num // _gcd, den // _gcd


def reduce_root(index, radicand):
    """
    reduce root:
    - reduce index
    - bring terms out of root

    :param index: index int
    :param radicand: radicand int
    :return: reduced index and radicand
    """
