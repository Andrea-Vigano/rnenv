"""
file to store all the functions and procedures for RN object reduction
following the matrix_rn_representation protocol for reduction
"""

from numpy import array
from numpy import ndarray, unique, vstack, sum, logical_and, concatenate
from fractions import Fraction
from rnenv.rn.mathfuncs.funcs import factorization, build_factorized, gcd, are_proportional
from rnenv.rn.linearsops import linears_product, linear_conjugate


def reduce_rn(rn_array: ndarray):
    """
    Reduce real number 'rn' by following the matrix_rn_representation protocol
    for reduction.

    This function call the reduction function for the numerator and denominator,
    which calls the reducer for linears matrices, which again calls the reducer
    for the rn_unit object.

    Protocol reference:

    =====================
    REAL NUMBER REDUCTION
    =====================
        reduction of the real number (executed after the reduction of num and den)
        Parse for special cases:
        -> if den = 0: raise ZeroDivisionError
        -> if num = 0: set den to 1 no matter what

    parse num and den matrices to have the same length

    :param rn_array: Real Number array
    :return: reduced Real Number
    """

    num, den = __parse_num_den(rn_array[0], rn_array[1])
    if den[0, 0] == 0:
        raise ZeroDivisionError('Invalid real number denominator, cannot be equal to zero')
    elif num[0, 0] == 0:
        den = array([1, 1, 1])

    # fill size difference
    num, den = fill_size_difference(num, den)

    return array([num, den])


def fill_size_difference(a: ndarray, b: ndarray):
    """
    fill the difference in length between a and b with [0, 1, 1] arrays

    :param a: linear array
    :param b: linear array
    :return:  filled arrays
    """

    # make num and den to have the same length
    diff = abs(len(a) - len(b))
    filler = array([[0, 1, 1] * diff])
    filler.resize((3, ))
    if diff > 0:
        # num bigger
        b = vstack((b, filler))
    elif diff < 0:
        # den bigger
        a = vstack((a, filler))
    return a, b


def __parse_num_den(num:  ndarray, den: ndarray):
    """
    Reduce the two linears objects as a single item

    The reduction follows the matrix_rn_representation protocol:

    =======================
    INTER-LINEARS REDUCTION
    =======================
        -> checks for possible reductions between numerator and denominator

        -> get gcd of all the coefficients Ns
        -> if gcd != 1:
            divide every coefficient by gcd
        parse for inter-units correspondence (use 3 if statement to get faster computation if no match is found)
        -> if num and den have the same length:
            -> if they have the same 1-2 (same irrationals part, already ordered in the same way)
                -> if they have proportional coefficients (last as it is the heavier to perform)
                    (using mathfuncs.are_proportional)
                    -> build new array like num = factor and den = 1 (rearranging values if factor is not integer)
        rationalize denominator where possible
        -> if any index in denominator is greater than 1 and its length is less than 3
            there two cases in which it is possible to rationalize the denominator
            @ den is composed by one single root
            -> if length of den equal to 1 (so it is rational):
                -> multiply num by [1, den radical, den index - 1]
                -> move den radical to coefficient and set 1-2 = 1
            @ den is composed by two units, where the max index is 2
            -> if the indexes are all less than 3: (len must be 2)
                -> get the conjugate of den
                -> multiply both num by that conjugate
                instead of multiplying den by its conjugate, will try to
                get its value without performing the mul, for a better
                performance.
                -> parse the two units of den and:
                for each unit
                sum (coefficient ** 2) * radicand
                den = sum
        return num and den

    :param num: numerator linear 3 x N matrix
    :param den: denominator linear 3 x N matrix
    :return: reduced num and den
    """

    # reduce each linear as a separated object
    num = __reduce_linear(num)
    den = __reduce_linear(den)

    # reduction algorithm
    num, den = __reduce_num_den(num, den)
    # rationalize denominator where possible
    # check if there are irrationals in den and length is less that 3 before function call
    if den[den[:, 2] > 1].any() and len(den) < 3:
        num, den = __rationalize_num_den(num, den)
    return num, den


def __parse_index(num, den, index):
    """
    Parse super RN index, check of possible reductions between num, den and index

    Following the matrix_rn_representation protocol:

        INDEX REDUCTION

        for each linear:
        if linear length is 1

    :param num:
    :param den:
    :param index:
    :return:
    """

    pass


def __reduce_num_den(num: ndarray, den: ndarray):
    """
    SOLO NUM AND DEN REDUCER

    Numerator and denominator are reduced (but not parsed) following the matrix_rn_representation protocol

    :param num: numerator array
    :param den: denominator array
    :return: reduced num and den
    """

    # parse gcd
    num_coef = num[:, 0]
    den_coef = den[:, 0]
    _gcd = gcd(concatenate([num_coef, den_coef]))
    if _gcd != 1:
        num[:, 0] = num_coef // _gcd
        den[:, 0] = den_coef // _gcd

    # parse for inter-units correspondence
    if len(num) == len(den):
        if (num[:, 1:] == den[:, 1:]).all():
            proportional = are_proportional(num[:, 0], den[:, 0])
            if proportional:
                # build new array from factor
                factor = int(num[:, 0][0]) / int(den[:, 0][0])
                # if factor is float -> turn to integer ratio
                if round(factor, 5) == int(factor):
                    num = array([[int(factor), 1, 1]])
                    den = array([[1, 1, 1]])
                else:
                    factor = Fraction(int(num[:, 0][0]), int(den[:, 0][0]))
                    num = array([[factor.numerator, 1, 1]])
                    den = array([[factor.denominator, 1, 1]])
    return num, den


def __rationalize_num_den(num: ndarray, den: ndarray):
    """
    SOLO NUM AND DEN RATIONALIZE

    Tries to rationalize denominator with some common procedures, following the
    matrix_rn_representation protocol

    :param num: numerator array
    :param den: denominator array
    :return: rationalized num and den
    """

    # if this function is called, it means there is at least one irrational value in den
    # two cases
    # case 1
    if len(den) == 1:
        num = __reduce_linear(linears_product(num, array([[1, den[0, 1], den[0, 2] - 1]])))
        den = array([[den[0, 1], 1, 1]])
    # case 2
    # if len is not 1, then it is 2 because function is called if len(den) < 3
    elif (den[:, 2] < 3).all():
        cj = linear_conjugate(den)
        num = __reduce_linear(linears_product(num, cj))
        # parse den units
        _den = []
        for unit in den:
            _den.append((unit[0] ** 2) * unit[1])
        den = array([[_den[0] - _den[1], 1, 1]])
    return num, den


def __reduce_linear(linear: ndarray):
    """
    Reduce a linear, so an object like NUM and DEN, represented as a 3 x N matrix, where each row
    store the information of a single unit (like 3, 2 sqr(2) ...)

    The reduction follows the matrix_rn_representation protocol:

    after unit parsing, we can proceed to parse the entire linear object
    ==============================
    LINEAR UNITS MERGING ALGORITHM
    ==============================
        -> array manipulation

        assign new empty array
        get unique values in cols 1 and 2 (second and third)

        nested loop uniques and get all the rows with same 1-2 elements
            -> get the sum of all the pos = 0 values with that specific pos 1,2 values pattern
            -> if the 0 value is not null:
                -> stack the sum value on the new array
        return null array if the shape is (3,)
        order linear by M, L sizes

        return reduced data array
    ==============================

    :type linear: ndarray or list
    :param linear: linear 3 x N matrix
    :return: reduced linear
    """

    # reduce linear units
    # for better performance, it may be better to move the loop inside the function called
    for p, unit in enumerate(linear):
        linear[p] = __reduce_unit(unit)

    # parse entire linear matrix
    # merge similar units (same rad and index)
    # merging algorithm
    # TODO look up for a better linear units merging algorithm

    arr, unq_one, unq_two = array([0, 0, 0]), unique(linear[:, 1]), unique(linear[:, 2])
    for one in unq_one:
        for two in unq_two:
            # get the sum of the columns that respect the condition determined by the loops
            s = sum(linear[logical_and(linear[:, 1] == one, linear[:, 2] == two)][:, 0])
            if s:
                arr = vstack((arr, [s, one, two]))
    # check arr is not a zero
    if arr.shape == (3,):
        return array([[0, 0, 1]])
    # order linear by 1-2 sizes
    arr = arr[arr[:, 2].argsort()]
    arr = arr[arr[:, 1].argsort()]
    return arr[1:]


def __reduce_unit(unit: ndarray or list) -> ndarray or list:
    """
    Reduce a single unit by itself following the matrix_rn_representation protocol:

    a unit is an integers triad referring to different aspects of itself
        +-------------+----------+-------+
        |      0      |     1    |   2   |
        +-------------+----------+-------+
        | coefficient | radicand | index |
        +-------------+----------+-------+

        so depending of this numbers we'll have different parsing possibilities

        if every parameter is integer -> First level RN:

        =======================
        INTEGERS UNIT REDUCTION
        =======================
        -> if N = 0: return 0, 0, 1
        -> parse CE
            -> L = 0: ValueError
            -> L is even and M < 0: ValueError
            -> L < 0 and M = 0: Value Error
        -> Parse 'special types' (easy - fast parse)
            -> L = 1: N *= M, M = 1
            -> M = 1, -1: N *= M, M = 1
        -> Parse L and factorized M's exponents ot be primes
            (using mathfuncs.factorization / .gcd)
            -> if gcd (exponents, L) != 1:
                -> divide exponents and L by gcd
        -> Parse to bring factors out of root
            loop trough factorized M:
                -> if factor exponent is greater than index:
                    -> N *= factor ** (int division between exponent and L)
                    -> exponent = module between exponent and L
                    (this way we avoid having to loop multiple times trough factors to be sure
                    that parsing is complete, because we ensure that the factor moved out of the root
                    is the greater possible)
        -> re build M from parsed factorized (using a flag to track eventual sign)
        -> Parse 'special types' (easy - fast parse)
            -> L = 1: N *= M, M = 1
            -> M = 1, -1: N *= M, M = 1
        =======================

        else -> N level RN:
            ->

    :param unit: array or list 3 x 1
    :return: reduced unit
    """

    # won't validate parameters (lower level methods used only by RN class)
    # TODO add nested RN reduction handling (and update protocol)
    # if only integers in array -> INTEGERS UNIT REDUCTION protocol
    if unit.dtype == int:
        unit = __reduce_integer_unit(unit)
    else:
        pass
    return unit


# Integer Radical Reduction (probably temp)
class __IRR:
    """
    Methods storage for Integers unit reduction
    contains:
        radical_exc -> validate radical values
        special_cases -> look for some specific and fast-to-parse values combinations
    """

    @staticmethod
    def radical_exc(rad: int, index: int):
        """
        Radicals CE
        -> even index and negative radical
        -> null index
        -> negative index and radical equal to 0

        Can raise ValueError if a condition is matched

        :param rad: radical integer
        :param index: index integer
        :return: None
        """

        if not index % 2 and rad < 0:
            raise ValueError('Invalid root, even index {} and negative radicand {}'.format(index, rad))
        elif index == 0:
            raise ValueError('Invalid root, index = 0')
        elif index < 0 and rad == 0:
            raise ValueError('Invalid root, negative index {} and radical = 0'.format(index))

    @staticmethod
    def special_cases(coefficient: int, rad: int, index: int):
        """
        Look for some special patterns that can reduce computation time
        and code complexity in general
        -> index equal to 1
        -> radicand equal to 0, 1, -1

        :param coefficient: coefficient integer
        :param rad: radical integer
        :param index: index integer
        :return: radical integer triad
        """

        # index == 1
        # rad == 1, 0
        if index == 1:
            return [coefficient * rad, 1, 1]
        elif rad in (0, 1, -1):
            return [coefficient * rad, 1, 1]
        else:
            return [coefficient, rad, index]


def __reduce_integer_unit(unit: ndarray or list) -> ndarray or list:
    """
    SOLO INTEGER UNIT reducer

    :param unit: array or list 3 x 1
    :return: reduced unit
    """

    # won't validate
    # FOLLOWS PROTOCOL ALGORITHM

    # check if 0 (avoid useless ops)
    if unit[0] == 0:
        return [0, 0, 1]
    # CE (for integer indexes)
    __IRR.radical_exc(unit[1], unit[2])
    unit = __IRR.special_cases(*unit)

    # get index and factorized radical exponents to be primes
    sign_flag, factorized = unit[1] < 0, factorization(unit[1])
    _gcd = gcd([factorized[f] for f in factorized] + [unit[2]])
    if _gcd != 1:
        factorized = {f: int(factorized[f] / _gcd) for f in factorized}
        unit[2] //= _gcd

    # parse to bring factor out of the root where possible
    for f in factorized:
        if abs(unit[2]) < factorized[f]:
            unit[0] *= f ** (factorized[f] // unit[2])
            factorized[f] %= unit[2]

    # rebuild radical with new factors
    unit[1] = build_factorized(factorized) * -1 if sign_flag else build_factorized(factorized)
    # final checks
    unit = __IRR.special_cases(*unit)
    # return
    return unit


if __name__ == '__main__':
    # some fast testing
    # generate random linears data and parse it
    from random import randint

    # 3 x N matrix

    data = [array([array([randint(-20, 20), randint(0, 5), randint(1, 3)]) for _ in range(randint(1, 10))])
            for _ in range(1000)]
    # test parsing
    for lin in data:
        print('Starting linear:\n {}'.format(lin))
        print('Parsed data:\n {}\n'.format(__reduce_linear(lin)))

    print(__reduce_linear(array([[-4, 1, 1], [4, 1, 2]])))

    print(__reduce_num_den(array([[4, 2, 2],
                                  [-4, 1, 1]]),
                           array([[2, 2, 2],
                                  [-2, 1, 1]])))

    print(__rationalize_num_den(array([[1, 1, 1]]),
                                array([[4, 1, 1],
                                       [2, 2, 2]])))
