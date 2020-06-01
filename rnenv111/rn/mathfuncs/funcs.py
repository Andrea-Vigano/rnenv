"""
Functions storage
"""

from math import gcd
from itertools import chain, count
from functools import reduce


def reduce_fraction(num: int, den: int):
    """
    reduce fraction to prime terms

    :param num: numerator int
    :param den: denominator int
    :return: reduced num and den
    """
    _gcd = gcd(num, den)
    return num // _gcd, den // _gcd


def multi_gcd(int_list: list) -> int:
    """
    returns the gcd of the integers inside the passed list

    :param int_list: integer list
    :return: gcd
    """
    return reduce(gcd, int_list) if 0 not in int_list else 1


def factorization_generator(n: int):
    """
    Generator that yield each prime factor of n (actually abs(n), which is the same)

    :param n: integer
    :return: integers factors
    """
    # assert positive
    n = abs(n)
    # if n == 0 or n == 1 -> return
    if n in [0, 1]:
        yield n
    stop = n ** 0.5 + 2
    # loop trough possible factors until n is totally consumed (n >= 1)
    for i in chain([2], count(3, 2)):
        if n <= 1:
            break
        if i > stop:
            yield n
            break
        while n % i == 0:
            n //= i
            yield i


def factorization(n: int) -> dict:
    """
    Function that returns a dictionary representing the factorized form of abs(n),
    Its used to check whether two numbers can be reduced, so it is useful to return a non-ordered
    data structure like a dictionary other than a list or generator

    :param n:  integer
    :return: dict of factors: exponent
    """
    f = {}
    for factor in factorization_generator(n):
        try:
            f[factor] += 1
        except KeyError:
            f[factor] = 1
    return f


def build_factorized(factorized: dict) -> int:
    """
    Build integer from its factorized form, (reverse function of factorization)
    :param factorized: factorized integer dict
    :return: integer
    """
    num = 1
    for factor in factorized:
        num *= factor ** factorized[factor]
    return int(num)


def reduce_root(index: int, radicand: int):
    """
    reduce root:
    - reduce index
        factorize radicand, and get gcd with index too.
        divide everything for gcd

    - bring terms out of root
        check if exponent factor (looping trough factorization factors)
        is divisible for index
        if so, divide exponent and bring term out of the root in an external factor

    :param index: index int
    :param radicand: radicand int
    :return: reduced index and radicand
    """

    # reduce index
    factorized = factorization(radicand)
    _gcd = multi_gcd([factorized[f] for f in factorized] + [index])
    if _gcd != 1:
        factorized = {f: int(factorized[f] / _gcd) for f in factorized}
        index //= _gcd

    # bring terms out of root
    mul_factor = 1
    for f in factorized:
        if abs(index) < factorized[f]:
            mul_factor *= f ** (factorized[f] // index)
            factorized[f] %= index

    # rebuild radical with new factors
    radicand = build_factorized(factorized)

    return mul_factor, index, radicand
