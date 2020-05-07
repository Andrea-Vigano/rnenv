"""
side package to store some useful functions for more complex integers manipulation
like factorization, check if two numbers are coprimes, get fast GCD and LCM of two or more integers ecc
"""


# Imports
from itertools import chain, count


def is_prime(n: int):
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


def factorization(n: int):
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


if __name__ == '__main__':
    # performance testing
    from time import time

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

    t_factorization(39814)

    # test performances
    t_is_prime(3)
    t_is_prime(15)
    t_is_prime(3456)
    t_is_prime(24097)
    t_is_prime(328989423)
    t_is_prime(328989423394027189)
    print('\n')

    t_factorization(1)
    t_factorization(10)
    t_factorization(20)
    t_factorization(1000)
    t_factorization(39814)
    t_factorization(324579779428)
    t_factorization(1589832868687)
    t_factorization(158983286868760)
    print('\n')
