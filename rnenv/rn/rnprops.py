"""
file to store all the biggest properties methods for RN class
like str and repr for instance
"""

EC = ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']  # exponent chars


def rn_classification():
    pass


def rn_str(rn_array, index):
    """
    rn string representation protocol
    Will suppose the rn has already been reduced
    -> if den = 1 -> return str(num)
    -> if num = 0 -> return '0'
    else:
        -> get num and den strings
        -> compare their length and determine how long the fraction line is
           and the padding of the shortest linear
        -> parse index
            if 1 -> return like it is
            if 2 -> return '√(' + string + ')'
            else -> return 'ᴸ√(' + string + ')'
        -> build fraction like multi-linear string

    :return:
    """

    # TODO rewrite str code
    # TODO re define str protocol

    num = __linear_str(rn_array[0])
    str_index = __index_str(index)
    if num == '0':
        return '0'
    den = __linear_str(rn_array[1])
    if den == '1':
        if len(rn_array[0]) == 1:
            return str_index + num
        return str_index + '(' + num + ')'
    diff = abs(len(num) - len(den))
    # build fraction
    if len(num) > len(den):
        line = '-' * len(num)
        pad = ' ' * (diff // 2)
        string = num + '\n' + line + '\n' + pad + den
    else:
        line = '-' * len(den)
        pad = ' ' * (diff // 2)
        string = pad + num + '\n' + line + den
    return str_index + '(' + string + ')'


def __index_str(index):
    """
    index string representation protocol
    if 1 -> return ''
    if 2 -> return '√'
    if 3 -> return 'ᴸ√'

    :param index: index
    :return: index string representation
    """
    if index == 1:
        return ''
    elif index == 2:
        return '√'
    else:
        return ''.join([EC[int(ch)] for ch in str(index)]) + '√'


def __linear_str(linear):
    """
    linear str representation protocol
    -> join each unit string (must add '+' in between if the unit is positive)

    :param linear: linear array
    :return: linear string representation
    """
    string = ''
    for p, unit in enumerate(linear):
        str_unit = __unit_str(unit)
        string += str_unit if str_unit[0] == '-' or p == 0 else '+' + str_unit
    return string if string else '0'


def __unit_str(unit):
    """
    unit str representation protocol
    Will suppose the unit has already been reduced (0 if N = 0)
    -> N = 0 -> return '' (return none so that the filler zeros at the end of linears do not interfere
                           with the string representation)
    -> else: L = 1 (then M should be 1 as well) -> return 'N'
    ->       L = 2 -> return 'N√M'
             else  -> return 'Nᴸ√M'
    :param unit: unit array
    :return: unit string representation
    """
    if unit[0] == 0:
        return ''
    elif unit[2] == 1:
        return str(unit[0])
    elif unit[2] == 2:
        return str(unit[0]) + '√' + str(unit[2])
    else:
        return str(unit[0]) + ''.join([EC[int(ch)] for ch in str(unit[2])]) + '√' + str(unit[1])


def __rn_repr():
    pass


if __name__ == '__main__':
    from numpy import array

    print(__unit_str([3, 2, 3]))
    print(__linear_str(array([[1, 3, 4],
                             [4, 3, 2],
                             [-6, 1, 1]])))
