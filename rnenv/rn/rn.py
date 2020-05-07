"""
============
rn.py module
============
-> define classes for real numbers representation
so that you can, for example, get the value of a sum of
radicals as a non-approximated real number
-> sqr(2) + sqr(2) = 2 * sqr(2) [as a single object] and not 2.828... float number
============

============
matrix_rn_representation.txt:
============
"""

# Imports


# Nestable real number class
class RN:
    """
    Real Number class

    -> nestable object (understands what it is from the args it gets)
    -> if only simple numbers (integers / floats) -> 'simple object'
    -> if other real numbers as well -> 'more complex real number'

    To represent irrational object an 'index' parameter is implemented, set to 1 by default.
    Calculations can be done between RNs and other atomic numeric types like integers and floats.
    For better performances, a property classifying the object by its complexity type, permitting to use different
    calculation methods for different objects, as general methods would probably be slower and overkill
    (most of the times)
    """

    # permitted arguments for num, den and index parameters (as str) and add list support
    PERMITTED_PARAMETERS = ['int', 'RN']
    PERMITTED_PARAMETERS.append('List[' + ' or '.join(PERMITTED_PARAMETERS) + ']')

    def __init__(self, num, den=1, index=1):
        """

        :param num: numerator parameter (can be int or RN)
        :param den: denominator parameter (can be int or RN but != 0)
        :param index: index of object, default set to one
        """

        # TODO set up float to fractions converter to permit float numbers to be passed as arguments (fractions.py?)
        #  must modify PERMITTED_PARAMETERS value and add 'float'

        # validate parameters
        # num / den -> valid if int or RN (den also if != 0)
        # index -> int or RN
        self.__validate_parameters(num, den, index)
        # simplify / reduce raw parameters

        # TODO set up reduction methods for num, den, index and num-den-index

        # set parameters
        self.num = num
        self.den = den
        self.index = index
        # classify self in a complexity-based hierarchy

    # define representation methods
    # objects are being automatically simplified during initialization so we can just iter through num and den list
    def __str__(self):
        """
        str(self)
        if index = 1 (default) -> won't wrap with root
        if index = 2 -> won't specify index
        if index != 2 -> specify index in square brackets at the start of string [index]√number
        if den = 1 (default) -> won't print it

        :return: str
        """

    def __validate_num(self, unit):
        """
        Validate num type
        Raises argument error

        :param unit: num (or den or index, as this method is also used by __validate_den and for index validation)
        :return: None
        """
        def val(item):
            if not (isinstance(item, int) or isinstance(item, RN)):
                raise ValueError('Bad user argument, must be {}, got {} instead'.format(self.PERMITTED_PARAMETERS,
                                                                                        type(item)))

        if isinstance(unit, list):
            for i in unit:
                val(i)
        else:
            val(unit)

    def __validate_den(self, den):
        """
        Validate den type and that den != 0
        use __validate_num to validate den type

        :param den: den
        :return: None
        """

        # TODO define __eq__ method for RN class

        # first check if __eq__ is defined
        if hasattr(den, __eq__):
            if den == 0:
                raise ValueError('Bad user argument, RN denominator cannot be zero')
        self.__validate_num(den)

    def __validate_parameters(self, num, den, index):
        # validate parameters by calling their specific methods
        self.__validate_num(num)
        self.__validate_den(den)
        self.__validate_num(index)

    def __classify(self):
        """
        Define the complexity level of self, useful to determine which methods / procedures should be used to
        operate with it, to save computation time a have a better performance in general
        ===========
        classes
        ===========
        RATIONALS
        integer => den = 1, index = 1, num is integer
        fraction => index = 1, den is integer, num is integer (rational number)
        IRRATIONALS
        simple root => index is integer, den = 1, num is integer

        :return: str
        """
