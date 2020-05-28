"""
class mask, data handler for the function rn in rn.py, used to permit a more user-friendly approach
to RN object instantiation
"""

# Imports
from fractions import Fraction
from decimal import Decimal
from numpy import array

from rnenv110.rn.mathfuncs.funcs import fraction_from_float


# mask class
class Mask:
    """
    RN mask class, gets the arguments passed at rn function at rn.py, parse them
    and return an RN object.

    Following the matrix_rn_representation:

        accepted parameters:
        INTEGER:
            int
        SINGLE UNIT INTEGER:
            int, int, int
        OTHERS:
            build as expression

        ALGORITHM:
            validate args
            args length = 1:
                integer
            args length = 3:
                single unit
    """

    PERMITTED_PARAMETERS = [('int', ), ('int', 'int', 'int')]
    PERMITTED_TYPES = [int, float, Fraction, Decimal]
    ERROR_MSG = 'Bad user argument, must be one of {}, got {} instead'

    def __init__(self, *args):
        """
        validate parameters,

        :param args: mask parameters
        """

        # validate parameters
        self.__validate_parameters(args)
        self.data = args

    def __validate_parameters(self, args):
        """
        validate that args match with one of the PERMITTED_PARAMETER

        :param args: arguments passed
        :return: None
        """

        if len(args) == 1 or len(args) == 3:
            if not all(isinstance(data, int) for data in args):
                raise ValueError(self.ERROR_MSG.format(self.PERMITTED_PARAMETERS, args))
        else:
            raise ValueError(self.ERROR_MSG.format(self.PERMITTED_PARAMETERS, args))

    def associated_rn(self):
        """
        Returns the actual real number array and index ready to
        instantiate the object

        if args length is 1:
            return integer
        else: (args length is 3)
            return unit

        :return: array
        """

        # parse args
        if len(self.data) == 1:
            ar = array([[[self.data[0], 1, 1]], [1, 1, 1]])
        else:
            ar = array([[[self.data[0], self.data[1], self.data[2]]], [[1, 1, 1]]])
        return ar
