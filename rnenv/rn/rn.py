"""
============
rn.py module
============
-> define classes for real numbers representation
so that you can, for example, get the value of a sum of
radicals as a non-approximated real number
-> sqr(2) + sqr(2) = 2 * sqr(2) [as a single object] and not 2.828... float number
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

    # permitted arguments for num, den and index parameters (as str)
    PERMITTED_PARAMETERS = ['int', 'RN']

    def __init__(self, num, den, index=1):
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
        # set parameters
        self.num = num
        self.den = den
        self.index = index

    def __validate_num(self, unit):
        """
        Validate num type
        Raises argument error

        :param unit: num (or den or index, as this method is also used by __validate_den and for index validation)
        :return: None
        """

        if not (isinstance(unit, int) or isinstance(unit, RN)):
            raise ValueError('Bad user argument, must be {}, got {} instead'.format(self.PERMITTED_PARAMETERS,
                                                                                    type(unit)))

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
