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
matrix_rn_representation.txt
============
"""

# Imports
from numpy import array as ar
from numpy import ndarray
from numpy import int_

from rnenv.rn.rnreduce import reduce_rn
from rnenv.rn.rnprops import rn_str, rn_classification
from rnenv.rn.rnops import rn_neg
from rnenv.rn.rnmask import Mask


# rn initialization mask
def rn(*args, index=1):
    """
    RN initialization mask to avoid the user to build the rn array by himself and permit an easier
    usage of the object in the end.

    Following the matrix_rn_representation protocol for rn masks.

    accepted parameters:
        INTEGER:
            int
        RATIONAL:
            int, int
            float
            Fraction
            Decimal
        SIMPLE IRRATIONAL:
            use index kw set to the root index
        MIXED IRRATIONAL:
            you may use actual sums and subs between the different units of the object you want to create
        COMPOSED IRRATIONAL:
            build as expression

        ALGORITHM:
            parse args:
                args length == 1:
                    int -> INTEGER
                    float -> RATIONAL
                    Fraction -> RATIONAL
                    Decimal -> RATIONAL
                args length == 2:
                    int, int -> RATIONAL

    :return: RN object
    """

    return RN(*(Mask(*args, index=index).associated_rn()))


# Nestable real number class
class RN:
    """
    Real Number class

    -> nestable object (understands what it is from the args it gets)
    -> if only simple numbers (integers) -> 'simple object'
    -> if other real numbers as well -> 'more complex real number'

    To represent irrational object an 'index' parameter is implemented, set to 1 by default.
    Calculations can be done between RNs and other atomic numeric types like integers and floats.
    For better performances, a property classifying the object by its complexity type, permitting to use different
    calculation methods for different objects, as general methods would probably be slower and overkill
    (most of the times)
    """

    # permitted arguments for num, den and index parameters (as str) and add list support
    PERMITTED_PARAMETERS = ('numpy.ndarray',)
    ARRAY_SIZES = (2, int(), 3)
    ARRAY_DIM = len(ARRAY_SIZES)
    PERMITTED_UNITS = ('int', 'RN')
    PERMITTED_INDEXES = PERMITTED_UNITS

    COMPATIBLE_TYPES = ('RN', 'int', 'float', 'Fraction', 'Decimal')

    def __init__(self, array, index=1):
        """
        # TODO rewrite matrix_rn_representation to include a specific clear protocol for matrix specs
        This method is not user friendly, it is intended to be called after a parameter parsing from the masks
        which permit a more intuitive object instantiation

        EXAMPLE:
        to init a '2', you may do: (ar is numpy.array)

        # >>> two = RN(ar([[2, 0, 0], [1, 0, 0]]))
        # >>> two == 2
            True

        this is obviously really complex for a simple integer, and that's why the usage of the masks is promoted

        :param array: 3d array representing the real number (following the protocol from matrix_rn_representation)
        :param index: index of the object, default set to one
        """

        # TODO set up float to fractions converter to permit float numbers to be passed as arguments (fractions.py?)
        #  must modify PERMITTED_PARAMETERS value and add 'float'

        # TODO set up RN main ops

        # TODO set up RN props
        
        # TODO set up nested RN object creation (when the RN class is already fully working for integers)

        # validate parameters
        # -> array dimensions, specs, data types and den != 0
        # -> index type
        self.__validate_array(array)
        self.__validate_den(array[1])
        self.__validate_index(index)

        # reduce data and assign to attributes
        self.array, self.__index = RN.__reduce(array, index)

        # classify object from a complexity based hierarchy
        self.__cls = self.__classify()

        # string storage attribute (initialized to empty string but updated when the str method is first called)
        # used to avoid having to build the string every time the method is called, permitting somewhat of
        # a performance boost
        self.__str = ''

    # define representation methods
    # objects are being automatically simplified during initialization
    def __str__(self):
        """
        str(self)
        following the matrix_rn_representation protocol for string rn representation

        using external functions in rn.rnprops

        :return: string representation
        """
        if not self.__str:
            self.__str = rn_str(self.array, self.__index, self.__cls)
        return self.__str

    def __repr__(self):
        """
        repr(self)

        :return: string representation
        """
        return str(self)

    # props getters
    @property
    def num(self):
        return self.array[0]

    @property
    def den(self):
        return self.array[1]

    @property
    def index(self):
        return self.__index

    @property
    def cls(self):
        return self.__cls

    # type casting methods
    def __int__(self):
        pass

    def __float__(self):
        pass

    def __bool__(self):
        pass

    # comparison methods
    # defined for
    # RN, int, float, [Fraction, Decimal]

    def __ne__(self, other):
        pass

    def __eq__(self, other):
        pass

    def __gt__(self, other):
        pass

    def __ge__(self, other):
        pass

    def __lt__(self, other):
        pass

    def __le__(self, other):
        pass

    # operations methods
    # defined for
    # RN, int, float, [Fraction, Decimal]

    def __neg__(self):
        """
        -self
        -> change the signs of the units in num

        :return: -self
        """
        return rn_neg(self)

    def __abs__(self):
        """
        |self|
        -> if self < 0, return -self
           else return self

        :return: abs(self)
        """
        pass

    def __add__(self, other):
        """
        self + other
        Operation is based on the classification of self and other
        (and the type of other)

        :param other:
        :return:
        """
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __truediv__(self, other):
        pass

    def __floordiv__(self, other):
        pass

    def __pow__(self, power, modulo=None):
        pass

    # local methods
    def __validate_array_type(self, array):
        """
        DOC at __validate_array

        :param array: array parameter
        :return: None
        """

        if not isinstance(array, ndarray):
            raise ValueError('Bad user argument, array parameter must be type {}, got {} instead'.format(
                self.PERMITTED_PARAMETERS, type(array)
            ))

    def __validate_array_sizes_conformity(self, array):
        """
        DOC at __validate_array

        :param array: array parameter
        :return: None
        """

        if len(array.shape) != 3:
            raise ValueError('Bad user argument, array must have {} dimensions, got {} instead'.format(
                self.ARRAY_DIM, len(array.shape)
            ))
        if array.shape[0] != 2:
            raise ValueError('Bad user argument, array must have a first dimension equal to {}, got {} instead'.format(
                self.ARRAY_SIZES[0], array.shape[0]
            ))
        if array.shape[2] != 3:
            raise ValueError('Bad user argument, array must have a first dimension equal to {}, got {} instead'.format(
                self.ARRAY_SIZES[2], array.shape[2]
            ))

    def __validate_array_data_types(self, array):
        """
        DOC at __validate_array

        :param array: array parameter
        :return: None
        """

        for unit in array.flat:
            if not (isinstance(unit, int) or isinstance(unit, RN) or isinstance(unit, int_)):
                raise ValueError('Bad user argument, every item in array must be {}, got {} instead'.format(
                    self.PERMITTED_UNITS, type(unit)
                ))

    def __validate_array(self, array):
        """
        Validate some array specs:
        -> is instance of numpy.ndarray (array type)
        -> sizes conformity to the matrix_rn_representation protocol (2 x N x 3)
        -> data types of the array

        using sub methods __validate_array_[type, sizes_conformity, data_types] to split the different tasks around
        and improve code legibility

        :param array: array passed as parameter
        :return: None
        """

        # validate array type
        self.__validate_array_type(array)
        # validate sizes conformity (2 x N x 3)
        self.__validate_array_sizes_conformity(array)
        # validate data types
        self.__validate_array_data_types(array)

    @staticmethod
    def __validate_den(den):
        """
        Validate that den != 0
        (this check is performed also after the reduction, it is done here to avoid
        wasting computation time in operations which can be stopped here)

        linear matrix, following the matrix_rn_representation, is equal to zero when:
            den = [[0, M, L]] or [[N, 0, L]]

        :param den: den (as a matrix 3 x N)
        :return: None
        """

        # den is a 3 x N array (other wise it would have raised an error at __validate_array)
        if len(den) == 1:
            if den[0, 0] == 0 or den[0, 1] == 0:
                raise ValueError('Bad user argument, RN denominator cannot be zero')

    def __validate_index(self, index):
        """
        Validate index type

        :param index: index parameter
        :return: None
        """

        if not (isinstance(index, int) or isinstance(index, RN)):
            raise ValueError('Bad user argument, RN index must be {}, got {} instead'.format(
                self.PERMITTED_INDEXES, type(index)
            ))

    def __classify(self):
        """
        Define the complexity level of self, useful to determine which methods / procedures should be used to
        operate with it, to save computation time a have a better performance in general

        Following the matrix_rn_representation protocol:

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

        using an external function from rn.rnprops

        :return: str
        """

        # TODO set up classification method (and then rewrite str methods)

        return rn_classification(self.array)

    @staticmethod
    def __reduce(array, index):
        """
        reduce object with array manipulation following the protocol at matrix_rn_representation.txt
        -> reduce all
            -> reduce each linear (num and den)
                -> reduce each unit (N)
                    Actual parsing start
                    -> parse from parameters (3)
                -> reduce unit
            -> reduce linear
        -> reduce all
        The actual functions performing the reduction are store inside rnreduce.py

        :param array: object array
        :param index: object index
        :return: reduced array parameter
        """

        array, index = reduce_rn(array[0], array[1], index)
        return array, index


if __name__ == '__main__':
    a = ar([[[1, 2, 2], [1, 3, 2]], [[4, 1, 1], [1, 3, 2]]])
    r = RN(a, 1)
    a = rn(2, 3)
