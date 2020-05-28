"""
Functions storage
"""

from numpy import broadcast_arrays, nonzero


def gcd(a, b):
    """
    Fast gcd getter

    :param a: integer
    :param b: integer
    :return: GCD of a and b
    """
    a, b = broadcast_arrays(a, b)
    a = a.copy()
    b = b.copy()
    pos = nonzero(b)[0]
    while len(pos) > 0:
        b2 = b[pos]
        a[pos], b[pos] = b2, a[pos] % b2
        pos = pos[b[pos]!=0]
    return a
