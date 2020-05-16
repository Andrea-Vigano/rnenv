"""
class mask, data handler for the function rn in rn.py, used to permit a more user-friendly approach
to RN object instantiation
"""

# Imports
from fractions import Fraction
from decimal import Decimal
from numpy import array

from rnenv.rn.mathfuncs.funcs import fraction_from_float


# mask class
class Mask:
    """
    RN mask class, gets the arguments passed at rn function at rn.py, parse them
    and return an RN object.

    Following the matrix_rn_representation:

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
    """

    PERMITTED_PARAMETERS = [('int', ), ('int', 'int'), ('float', ), ('Fraction', ), ('Decimal', )]
    PERMITTED_TYPES = [int, float, Fraction, Decimal]
    ERROR_MSG = 'Bad user argument, must be one of {}, got {} instead'

    def __init__(self, *args, index):
        """
        validate parameters,
        won't validate index as it is already validated at RN

        :param args: mask parameters
        :param index: index int or RN
        """

        # validate parameters
        self.__validate_parameters(args)
        self.data = args
        self.index = index

    def __validate_parameters(self, args):
        """
        validate that args match with one of the PERMITTED_PARAMETER

        :param args: arguments passed
        :return: None
        """

        if len(args) == 2:
            if not (isinstance(args[0], int) and isinstance(args[1], int)):
                raise ValueError(self.ERROR_MSG.format(self.PERMITTED_PARAMETERS, args))
        elif len(args) == 1:
            if not any(isinstance(args[0], tp) for tp in self.PERMITTED_TYPES):
                raise ValueError(self.ERROR_MSG.format(self.PERMITTED_PARAMETERS, args))

    def associated_rn(self):
        """
        Returns the actual real number array and index ready to
        instantiate the object

        if args length is 2:
            build array from 2 integers
        else:
            if int:
                build int rn array
            if float:
                use fraction_from_float
            if Fraction:
                use numerator and denominator attributes
            if Decimal:
                cast to fractions

        :return: array, index
        """

        # parse args
        if len(self.data) == 1:
            if isinstance(self.data[0], int):
                self.data = (self.data[0], 1)
            elif isinstance(self.data[0], float):
                self.data = fraction_from_float(self.data[0])
            elif isinstance(self.data[0], Fraction):
                self.data = (self.data[0].numerator, self.data[0].denomiator)
            elif isinstance(self.data[0], Decimal):
                fr = Fraction(self.data[0])
                fr.limit_denominator(100000000)
                self.data = (fr.numerator, fr.denominator)
        # build array
        ar = array([[[self.data[0], 1, 1]],
                    [[self.data[1], 1, 1]]])
        return ar, self.index
