"""
file to store all the biggest properties methods for RN class
like str and repr for instance
"""

from numpy import int_

EC = ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']  # exponent chars


def rn_classification(array):
    """
    Real number classification algorithm following the matrix_rn_representation protocol

    ==========================
    REAL NUMBER CLASSIFICATION
    ==========================

        Protocol for real numbers classification, to permit the usage of faster algorithms in special cases

        @ no denominator
        :INTEGER
        @ denominator
        :FRACTION

        @ linears specs (determined for num and den)
        RATIONAL
        SIMPLE IRRATIONAL
        MIXED IRRATIONAL
        COMPOSED IRRATIONAL

        -> total of 8 possible cases
            INTEGER -> den = 1
            FRACTION -> else

            RATIONAL -> in num and den M = 1
            SIMPLE IRRATIONAL -> len(num) = 1 (and not rational)
            MIXED IRRATIONAL -> num and den data type = int (and not simple irrational)
            COMPOSED IRRATIONAL -> else

    :return: classification strings list
    """
    _class = ['', '', '']

    # integer / fraction
    # den length == 1 and den = [1, 1, 1]
    if len(array[1]) == 1 and (array[1][0] == 1).all():
        _class[0] = 'integer'
    else:
        _class[0] = 'fraction'

    # rational / irrational for each linear
    for p, lin in enumerate(array):
        if (lin[:, 1:] == 1).all():
            _class[p + 1] = 'rational'
        elif len(lin) == 1 and p == 0:
            # den cannot be simple irrational
            _class[p + 1] = 'simple irrational'
        elif lin.dtype == int_:
            _class[p + 1] = 'mixed irrational'
        else:
            _class[p + 1] = 'composed irrational'
        # if first-type class is 'integer', won't parse for denominator
        if _class[0] == 'integer':
            break
    return _class


def rn_str(array, cls):
    """
    String representation builder for RN objects.
    Following the matrix_rn_representation protocol for string representation:

        Will relate to the object class to determine if some part of the algorithm can be avoided or not

        If the object has a first-type class of INTEGER, only the numerator will be build,
        as we already know that the denominator is equal to 1.
        The actual string building is done by sub modules called by this one.

        ALGORITHM:
            parse num
            if FRACTION:
                parse den
                parse index
                build fraction string
                return full string
            return num string

            Where 'parse' indicates the call to __linear_str function
            Where 'parse index' is the call of the function __root_str

    :param array: object array
    :param cls: object classification data (complexity based)
    :return: string representation
    """
    num, den = array[0], array[1]
    num_str = __linear_str(num, integer=bool(cls[1] == 'rational'))
    if cls[0] == 'fraction':
        den_str = __linear_str(den, integer=bool(cls[2] == 'rational'))
        # build fraction string representation
        return '(' + num_str + ')/(' + den_str + ')'
    return num_str


def __linear_str(lin, integer=False):
    """
    Parse linear matrix to get its string representation.
    Following the matrix_rn_representation protocol for string representation:

        If the classification of the linear is an integer we will return the integer value string
        otherwise we will parse the lin by calling an external builder method.

        ALGORITHM:
            If integer:
                return the first item in the matrix as string
            parse lin
            return lin string

            Where 'parse' indicates the call to the external method __complex_linear_str

    :param lin: linear matrix
    :param integer: bool value, True if the linear is an integer
    :return: string representation
    """
    if integer:
        return str(lin[0, 0])
    return __complex_linear_str(lin)


def __complex_linear_str(lin):
    """
    Parse complex linear matrix to get its string representation
    Following the matrix_rn_representation protocol for string representation:

        Parse units one by one by looping trough lin, build the string by checking for
        some specs in the unit array, if the radicand is 1, build as an integer, else,
        if the index is 2, build a square root (with a coefficient if it is not 1), else,
        build an nth-root, by using the exponent unicode characters if the index is an integer, otherwise
        will print it in round brackets close to the root.

        The index parsing is actually done from an external module.

        If any item in the unit is an RN, the method, by calling RN.__str__ will get the correct
        nested RN representation of the eventual nested real numbers objects.

        ALGORITHM:
            Looping trough units

            If coefficient is 0:
                return 0
            else if the radicand is 1:
                return coefficient string
            else:
                return (parse index) + radicand (if coefficient equal 1)

        Where 'parse index' is the call of the function __root_str

    :param lin: complex linear matrix
    :return: string representation
    """
    # main loop
    string = ''
    for unit in lin:
        if unit[0] == 0:
            if len(lin) == 1:
                string = '0'
            # else do nothing because it is a filler
        elif unit[1] == 1:
            string += str(unit[0])
        else:
            if unit[0] == 1:
                unit_str = __root_str(unit[2]) + str(unit[1])
            elif unit[0] == -1:
                unit_str = '-' + __root_str(unit[2]) + str(unit[1])
            else:
                unit_str = str(unit[0]) + __root_str(unit[2]) + str(unit[1])
            string = string + unit_str if unit_str[0] == '-' else string + '+' + unit_str
    return string


def __root_str(index):
    """
    Build index string
    Following the matrix_rn_representation protocol for string representation:

        If the index is 1, will return an empty string, if it is 2, will return a simple root char,
        else if it is and integer, will use the exponents unicode chars, if it is a complex RN, will
        print it aside the root in rounded brackets

        ALGORITHM:
            If index is 1:
                return ''
            else if index is 2:
                return √
            else:
                if index is integer:
                    use exponents chars
                else:
                    build string with index aside root in rounded brackets

    :param index: index (int or RN)
    :return: string representation of the root with index equal to the one passed
    """
    if index == 1:
        return ''
    elif index == 2:
        return '√'
    elif isinstance(index, int) or isinstance(index, int_):
        return ''.join([EC[int(ch)] for ch in str(index)]) + '√'
    else:
        return '(' + str(index) + ')' + '√'


if __name__ == '__main__':
    from numpy import array as ar

    print(__linear_str(ar([[1, 3, 4],
                           [4, 3, 2],
                           [-6, 1, 1]])))
