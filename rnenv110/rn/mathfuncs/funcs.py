"""
side package to store some useful functions for more complex integers manipulation
like factorization, check if two numbers are coprimes, get fast GCD and LCM of two or more integers ecc
"""


# Imports
from itertools import chain, count
from math import gcd as math_gcd
from functools import reduce
from fractions import Fraction
from numpy import ndarray


def is_prime(n: int) -> bool:
    """

    :param n: integer
    :return: True if the number is prime, False is not
    """
    n = abs(n)
    if n < 3 or n % 2 == 0:
        return n == 2
    else:
        return not any(n % i == 0 for i in range(3, int(n**0.5 + 2), 2))


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


def gcd(int_list: list or ndarray) -> int:
    """
    returns the gcd of the integers inside the passed list

    :param int_list: integer list
    :return: gcd
    """
    return reduce(math_gcd, int_list) if 0 not in int_list else 1


def are_proportional(a: list or ndarray, b: list or ndarray) -> (bool, float):
    """
    calculate whether the integers in the lists are proportional
    returns True if lists are proportional
            False if lists are not proportional

    :param a: integer list
    :param b: integer list
    :return: boolean
    """
    # to get better performances we won't validate the parameters
    # get factor
    factor = a[0] / b[0]
    # know if lists are proportional with map() and all()
    if all(i for i in map(lambda n, m: True if n / m == factor else False, a, b)):
        return True
    return False


def fraction_from_float(a: float) -> (int, int):
    """
    returns the fraction form of the float number a
    uses Fraction class and string cash to get a precise integer ratio of a,
    avoiding floating point imprecision

    :param a: float number
    :return: numerator and denominator integers of the fraction
    """

    # get a to be integer by multiplying by tens until it is integer
    f = Fraction(str(a))
    f.limit_denominator(100000000)
    return f.numerator, f.denominator


if __name__ == '__main__':
    # performance testing
    from time import time
    from random import randint

    # define @timer decorator
    def timer(func):
        def elapsed(*args, **kw):
            t_one = time()
            result = func(*args, **kw)
            t_two = time()
            print('Time elapsed to perform {} with parameter/s {}: {} s; result = {}'.format(
                func.__name__, [args, kw], t_two - t_one, result
            ))
            return result
        return elapsed

    # define timed functions
    t_is_prime = timer(is_prime)
    t_factorization = timer(factorization)
    t_build_factorized = timer(build_factorized)
    t_gcd = timer(gcd)
    t_are_proportional = timer(are_proportional)

    # test performances
    t_is_prime(3)
    t_is_prime(15)
    t_is_prime(3456)
    t_is_prime(24097)
    t_is_prime(328989423)
    t_is_prime(328989423394027189)
    print('\n')

    t_factorization(0)
    t_factorization(1)
    t_factorization(10)
    t_factorization(20)
    t_factorization(1000)
    t_factorization(39814)
    t_factorization(324579779428)
    t_factorization(1589832868687)
    t_factorization(158983286868760)
    print('\n')

    t_build_factorized({0: 1})
    t_build_factorized({1: 1})
    t_build_factorized({2: 1, 5: 1})
    t_build_factorized({2: 2, 5: 1})
    t_build_factorized({2: 3, 5: 3})
    t_build_factorized({2: 1, 17: 1, 1171: 1})
    t_build_factorized({2: 2, 9677: 1, 8385341: 1})
    t_build_factorized({7: 1, 17: 1, 53: 1, 499: 1, 505159: 1})
    t_build_factorized({2: 3, 5: 1, 131627: 1, 30195797: 1})
    print('\n')

    t_gcd([10, 34, 56, 56])
    t_gcd([325, 3456])
    t_gcd([5670294, 6970])
    t_gcd([58607, 485906, 383920, 283995])
    t_gcd([295068727589, 3849056903, 28340596902, 28450960])
    print('\n')

    for _ in range(10):
        num_ = randint(2, 20)
        a_, b_ = [randint(1, 100) for _ in range(num_)], [randint(1, 100) for _ in range(num_)]
        t_are_proportional(a_, b_)
    t_are_proportional([1, -2, 3, -4], [-2, 4, -6, 8])
