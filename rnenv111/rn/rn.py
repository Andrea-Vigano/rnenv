"""
RN 1.11 class module

Following the 'functional RN representation' protocol, based on the
dynamic representation of real numbers as a sequence of integers and operations that bind them.

Operations between numbers aren't new, they are normally performed by the language itself, but in the case of
mathematically represented real numbers, sometimes it is not possible to perform the operation required without a
loss in precision. Normally, this is not a big deal, but with this project our task is to permit a way to
represent real numbers and operate with them with no loss in precision.

This is made possible by checking if the operation required can be performed without a precision loss; if that is not
the case, the return value of the operation will be a real number storing the information of the operation that should
have been performed and the terms involved in that operations. This form of real number is valid and fully operative,
meaning you can use it as a normal and 'simple' real number object, permitting the representation of nested
structures we see in algebra.

For example, performing: √3 + √2 = 1.73 + 1.41 = 3.14 involve a certain level of approximation, because √3 and √2
are irrational. So, usually in algebra the sum is not performed in the first place, and the number is represented by
and expression, in this case, by two terms connected with '+', indicating a sum. So an object which aims to
algebraically represent numbers has to permit this kind of representation.
The example provided is a simple case, but the expression could also be more complex: if we were to divide the number
from the previous example by 2, we obviously would not be able to perform the operation; the number should then have
a form like:

    √3 + √2
    -------  --> 'TrueDiv( Add( Sqr( 3 ), Sqr( 2 ) ), 2 )'
       2

Which presents another level of complexity that has to be handled. Virtually, there is no limit to the amount of
complexity you can get to. To project this reality into a computable model, the RN object should be represented in two
main forms, strictly related to each other: the 'simple' RN, representable with a single integer, and the more complex
ones, which refer to an operation and its terms.

NOTE: in the example above, the numbers √3 and √2 fall into the second category, because their object should reference
the square root operation.
"""

# TODO redefine operations engine with the new functionalities added the RN class


from abc import ABCMeta, abstractmethod, ABC
from math import gcd
import math
from rnenv111.rn.mathfuncs.funcs import reduce_fraction


math = math


# op validator (used to assert that other is always an RN, even if integers are also accepted)
def _validate(func):
    def inner(self, other):
        # self is already RN
        if not (isinstance(other, RN) or isinstance(other, int)):
            raise ValueError('Unable to perform {} between {} (RN) and {} ({})'
                             .format(func, self, other, type(other)))
        if isinstance(other, int):
            other = RN(other)
        return func(self, other)

    return inner


class RN:
    """
    RN 'functional representation' class

    Following the functional RN representation protocol, as explained in the rn.py module DOC string.
    """

    # ACCEPTED / IMPLEMENTED OPERATIONS CLASSES
    PERMITTED_OPERATIONS = ()

    def __init__(self, *terms, op=None):
        """
        The type of RN instantiated depends from the parameters passed by the user:
        if the kw op is not specified (left as None), it will assume that self is a 'simple' RN (integer),
        and will expect ONLY one term of type int.

        if the op is specified, than it won't perform any validation, as it should have been done by the operator class,
        which validate the parameters relatively to the type of operation specified (for example, there are
        unary and binary operators...).

        Normally you should not specify operations, as this is done in the background by the operation methods of
        the class itself; for instance, the RN.__add__ method can tell if the terms of the operation can be
        simplified or should be left as they are. If that is the case, it will return an RN with the additional level
        of complexity needed.

        :param op: reference to the operator, set to None by default, does not need to be specified if you are
                   trying to represent an integer real number
        :param terms: terms of the instance, if no operator is specified, only one term needs to be passed, else
                      the number depends on the operator type.
        """

        if not op:
            # if no op -> simple RN
            if len(terms) != 1:
                raise ValueError('Bad user argument, RN where op is not specified should get 1 term, got {}'
                                 .format(terms))
            if not isinstance(terms[0], int):
                raise ValueError('Bad user argument, RN where op is not specified should get only int objects,'
                                 ' got {}'.format(type(terms[0])))

        self.op = op
        self.terms = terms

    # string representation
    def __str__(self):
        """
        If op is None, will return the string of the only term.
        Else, will use the string method defined in the op class

        :return: string representation of instance
        """

        if not self.op:
            return str(self[0])
        return self.op.string(self.terms)

    def __repr__(self):
        """
        repr(self)

        :return: string representation
        """

        return str(self)

    # data casing
    def __int__(self):
        """
        Integer cast to RN value, if no op, returns its only term
        else, truncate float(self), which actually calculate RN value recursively

        :return: Integer
        """

        return self[0] if not self.op else int(float(self))

    def __float__(self):
        """
        Float cast to RN value, if no op, returns its only terms cast to float
        else, recursively calculate the value of the RN by going up the different
        level of complexity in the representation of RN

        :return: Float
        """

        if not self.op:
            return float(self[0])
        else:
            flt_terms = tuple(map(lambda x: float(x), self.terms))
            func = self.op.__name__.lower() if not issubclass(self.op, ArithmeticOperation) \
                else '__' + self.op.__name__.lower() + '__'
            code_fragment = 'flt_terms[0].' + func + ('(*flt_terms[1:])' if flt_terms[1:] else '()')
            return float(eval(code_fragment))

    def __bool__(self):
        """
        Boolean cast to RN value, return False only is RN
        is equal to 0

        :return: Bool value
        """

        return self != 0

    # faster terms getter
    def __getitem__(self, item):
        """
        self[index]

        Won't validate because the index call at terms
        will handle errors by itself

        :param item: integer
        :return: object in terms (RN or int)
        """

        return self.terms[item]

    # evaluation
    @_validate
    def __eq__(self, other):
        """
        self == other

        :param other: RN or int
        :return: Boolean
        """

        if float(self) == float(other):
            return True
        return False

    # operations
    # Arithmetic operations: add, sub, mul, truediv, floordiv, pow, root (using matmul for that)

    # when the arguments make it to the actual function, they will always be RNs, as the decorator
    # __validate will convert them if any integer is found

    @_validate
    def __add__(self, other):
        """
        self + other

        :param other: RN (if int is turned to RN by __validate)
        :return: RN object sum
        """

        return Add(self, other).rv()

    @_validate
    def __sub__(self, other):
        """
        self - other

        :param other: RN (if int is turned to RN by __validate)
        :return: RN object difference
        """

        return Sub(self, other).rv()

    @_validate
    def __mul__(self, other):
        """
        self * other

        :param other: RN (if int is turned to RN by __validate)
        :return: RN object product
        """

        return Mul(self, other).rv()

    @_validate
    def __truediv__(self, other):
        """
        self / other

        :param other: RN (if int is turned to RN by __validate)
        :return: RN object quotient
        """

        return TrueDiv(self, other).rv()

    @_validate
    def __floordiv__(self, other):
        """
        self // other

        :param other: RN (if int is turned to RN by __validate)
        :return: RN object exact quotient
        """

        return FloorDiv(self, other).rv()

    @_validate
    def __pow__(self, power, modulo=None):
        return Pow(self, power).rv()

    @_validate
    def __matmul__(self, other):
        return MatMul(self, other).rv()


# Operation abstract class
class Operation(metaclass=ABCMeta):
    """
    Operation super - abstract class, interface that every operation class should follow:
    - OPERANDS_NUMBER attribute specifying how many terms are needed to perform the operation required
    - validation method of signature 'validate_terms(terms) -> None'
    - string representation method of signature 'string(terms) -> str'
    - return value getter of signature 'rv(self) -> RN'

    Every sub class of this is an 'operation class', meaning that every time the operation they refer to
    is performed, an instance of them is created to get the nature of the return value (if it is a 'simple' RN
    or another level of complexity is needed)

    The standard return value (rv) should be defined for when each term of the operation is 'simple' (no op),
    in the other cases, the rv should call a specific method from the Operation subclass, with a standardized name
    defined from the op types of the terms separated by an '_'. In this way, we are able to move the case specific
    code out of the rv method, making it easier to understand and modify. If the method is not defined, that it will
    assume that the operation it is trying to perform cannot be reduced, so it will return the standard RN object
    with another level of complexity to it.

    NOTE: the name of each operation should be (non caps sensitive) equal to the name of the function related to
    itself in RN class, for instance '__add__' -> class name should be 'Add'
    """

    PERMITTED_OPERANDS = (int, RN)
    # number of operands needed to perform operation
    # here set to NotImplemented but defined in subclasses
    OPERANDS_NUMBER = NotImplemented
    OPERATOR = NotImplemented

    def __init__(self, *terms):
        """
        Standard initialization of the operation:
        validate terms -> self.validate_terms
        set terms attribute, parsing every item so that there are only RN in the list

        :param terms: operation terms, their number vary depending on the operation performed
        """

        self.__validate_terms(terms)
        self.terms = tuple(map(lambda x: x if isinstance(x, RN) else RN(x), terms))

    def __validate_terms(self, terms):
        """
        Validate that the terms passed could be the operands of they operation type represented.
        If no, raise error.

        :param terms: RN operands
        :return: None
        """

        if len(terms) != self.OPERANDS_NUMBER:
            raise ValueError('Bad user argument, cannot perform operation {} with {} terms ({}), {} are needed'
                             .format(self.__class__.__name__, len(terms), terms, self.OPERANDS_NUMBER))
        for term in terms:
            if not any(isinstance(term, tp) for tp in self.PERMITTED_OPERANDS):
                raise ValueError('Bad user argument, operation {} can be performed only with types {},\n terms {}'
                                 ' contains one or more invalid type/s '
                                 .format(self.__class__.__name__, self.PERMITTED_OPERANDS, terms))

    @staticmethod
    @abstractmethod
    def string(terms):
        """
        Return the string representation of the operation, using the terms passed.

        :param terms: operation terms
        :return: string representation
        """

    def rv(self):
        """
        Return the actual RN object resulting from the operation,
        following the functional RN representation protocol.

        More detailed parsing is defined in the methods defined in the
        Operation subclasses.

        :return: RN object
        """

        # standard return value
        return RN(op=self.__class__, *self.terms)


# Arithmetic operations
# -> Add, Sub, Mul, TrueDiv, FloorDiv, Pow, Root
class ArithmeticOperation(Operation, ABC):
    """
    ABC super class for arithmetic operations, like Add, Sub, Mul...
    - define OPERANDS_NUMBER equal to 2
    - define a string method builder common for most of the operations
    - define a super rv method
    """

    OPERANDS_NUMBER = 2

    def __validate_terms(self, terms):
        super().__validate_terms(terms)

    @classmethod
    def string_builder(cls):
        """
        Returns a method that should return the string representation of the
        operation passed (using the cls.OPERATOR attribute)

        :return: string representation getter
        """

        def inner(terms):
            joint = ' ' + cls.OPERATOR + ' '
            return joint.join([str(term) for term in terms])
        return inner

    def rv(self):
        """
        Return RN return value of the operation
        for the arithmetic operations, in general, can perform operation in this cases:
            - if each term op is none

        if operation cannot be performed, return Operation rv method call

        :return: RN object
        """

        # call operator method
        try:
            # try to call the operation method for the terms defined operations
            op_1 = self.terms[0].op
            op_2 = self.terms[1].op
            op_1 = op_1.__name__.lower() if op_1 else 'none'
            op_2 = op_2.__name__.lower() if op_2 else 'none'
            return eval('self.' + op_1 + '_' + op_2 + '(self.terms)')
        except AttributeError:
            # no operation method found
            return super().rv()


class Add(ArithmeticOperation):

    OPERATOR = '+'

    @staticmethod
    def string(terms):
        return Add.string_builder()(terms)

    @staticmethod
    def none_none(terms):
        return RN(terms[0][0].__add__(terms[1][0]))

    @staticmethod
    def truediv_none(terms):
        """
        fraction + integer:
        - num + integer * den / den

        :return: RN object
        """

        num, den, integer = terms[0][0][0], terms[0][1][0], terms[1][0]
        data = (num + integer * den, den)
        return TrueDiv(*data).rv()

    @staticmethod
    def none_truediv(terms):
        return Add.truediv_none(tuple(reversed(terms)))

    @staticmethod
    def truediv_truediv(terms):
        """
        fraction + fraction
        - num1 * den2 + num2 * den1, den1 * den2

        :return: RN object
        """

        num_1, den_1, num_2, den_2 = terms[0][0][0], terms[0][1][0], terms[1][0][0], terms[1][1][0]
        data = (num_1 * den_2 + num_2 * den_1, den_1 * den_2)
        return TrueDiv(*data).rv()


class Sub(ArithmeticOperation):
    OPERATOR = '-'

    @staticmethod
    def string(terms):
        return Sub.string_builder()(terms)

    @staticmethod
    def none_none(terms):
        return RN(terms[0][0].__sub__(terms[1][0]))

    @staticmethod
    def truediv_none(terms):
        """
        fraction - integer:
        - num - integer * den / den

        :return: RN object
        """

        num, den, integer = terms[0][0][0], terms[0][1][0], terms[1][0]
        data = (num - integer * den, den)
        return TrueDiv(*data).rv()

    @staticmethod
    def none_truediv(terms):
        """
        integer - fraction:
        - integer * den - num / den

        :return: RN object
        """

        integer, num, den = terms[0][0], terms[1][0][0], terms[1][1][0]
        data = (integer * den - num, den)
        return TrueDiv(*data).rv()

    @staticmethod
    def truediv_truediv(terms):
        """
        fraction + fraction
        - num1 * den2 - num2 * den1, den1 * den2

        :return: RN object
        """

        num_1, den_1, num_2, den_2 = terms[0][0][0], terms[0][1][0], terms[1][0][0], terms[1][1][0]
        data = (num_1 * den_2 - num_2 * den_1, den_1 * den_2)
        return TrueDiv(*data).rv()


class Mul(ArithmeticOperation):
    OPERATOR = '*'

    @staticmethod
    def string(terms):
        return Mul.string_builder()(terms)

    @staticmethod
    def none_none(terms):
        return RN(terms[0][0].__mul__(terms[1][0]))

    @staticmethod
    def truediv_none(terms):
        """
        fraction * integer:
        - num * integer, den
        - reduce integer and den if possible

        :param terms:
        :return:
        """

        num, den, integer = terms[0][0][0], terms[0][1][0], terms[1][0]
        _gdc = gcd(integer, den)
        if _gdc != 1:
            integer //= _gdc
            den //= _gdc
        data = (num * integer, den)
        return TrueDiv(*data).rv()

    @staticmethod
    def none_truediv(terms):
        return Mul.truediv_none(tuple(reversed(terms)))

    @staticmethod
    def truediv_truediv(terms):
        """
        fraction * fraction:
        - num1 * num2, den1 * den2

        :param terms:
        :return:
        """

        num_1, den_1, num_2, den_2 = terms[0][0][0], terms[0][1][0], terms[1][0][0], terms[1][1][0]
        _gcd = gcd(num_1, den_2)
        if _gcd != 1:
            num_1 //= _gcd
            den_2 //= _gcd
        _gcd = gcd(num_2, den_1)
        if _gcd != 1:
            num_2 //= _gcd
            den_1 //= _gcd
        data = (num_1 * den_2, num_2 * den_1)
        return TrueDiv(*data).rv()


class TrueDiv(ArithmeticOperation):
    OPERATOR = '/'

    def __validate_terms(self, terms):
        """
        Override validation method
        - check that den is not 0

        :param terms:
        :return:
        """
        super().__validate_terms(terms)
        if terms[1] == 0:
            raise ZeroDivisionError('Bad user argument, cannot divide by zero')

    @staticmethod
    def string(terms):
        return TrueDiv.string_builder()(terms)

    @staticmethod
    def none_none(terms):
        """
        No op case: check if division can be performed completely, partially or not

        :return: RN object
        """
        num, den = reduce_fraction(terms[0].terms[0], terms[1].terms[0])
        if den == 1:
            return RN(num)
        data = (RN(num), RN(den))
        return RN(op=TrueDiv, *data)

    @staticmethod
    def truediv_none(terms):
        """
        fraction / integer

        :param terms: dividend and divisor
        :return: RN object
        """

        num, den, integer = terms[0][0][0], terms[0][1][0], terms[1][0]
        data = (num, den * integer)
        return TrueDiv(*data).rv()

    @staticmethod
    def none_truediv(terms):
        """
        integer / fraction

        :param terms: dividend and divisor
        :return: RN object
        """

        integer, num, den = terms[0][0], terms[1][0][0], terms[1][1][0]
        data = (integer * den, num)
        return TrueDiv(*data).rv()

    @staticmethod
    def truediv_truediv(terms):
        """
        fraction / fraction

        :param terms: dividend and divisor
        :return: RN object
        """

        num_1, den_1, num_2, den_2 = terms[0][0][0], terms[0][1][0], terms[1][0][0], terms[1][1][0]
        data = (num_1 * den_1, num_2 * den_2)
        return TrueDiv(*data).rv()


class FloorDiv(ArithmeticOperation):
    OPERATOR = '//'

    def __validate_terms(self, terms):
        """
        Override validation method
        - check that den is not 0

        :param terms:
        :return:
        """
        super().__validate_terms(terms)
        if terms[1] == 0:
            raise ZeroDivisionError('Bad user argument, cannot divide by zero')

    @staticmethod
    def string(terms):
        return FloorDiv.string_builder()(terms)

    @staticmethod
    def none_none(terms):
        return RN(terms[0][0].__floordiv__(terms[1][0]))

    @staticmethod
    def truediv_none(terms):
        """
        fraction // integer

        :param terms: dividend and divisor
        :return: RN object
        """

        data = ((terms[0][0][0] / terms[0][1][0]) // terms[1][0], )
        return RN(*data)

    @staticmethod
    def none_truediv(terms):
        """
        integer // fraction

        :param terms: dividend and divisor
        :return: RN object
        """

        data = ((terms[0][0]) // (terms[1][0][0] / terms[1][1][0]), )
        return RN(*data)

    @staticmethod
    def truediv_truediv(terms):
        """
        fraction // fraction

        :param terms: dividend and divisor
        :return: RN object
        """

        data = ((terms[0][0][0] / terms[0][1][0]) // (terms[1][0][0] / terms[1][1][0]), )
        return RN(*data)


class Pow(ArithmeticOperation):
    OPERATOR = '**'

    def __validate_terms(self, terms):
        """
        Validate pow terms:
        - exponent = 0 and base = 0
        - real exponent and base < 0
        are all cases where it is no possible to perform the operation

        :param terms: base and exponent
        :return: None
        """

    @staticmethod
    def string(terms):
        return Pow.string_builder()(terms)

    @staticmethod
    def none_none(terms):
        return RN(terms[0][0].__pow__(terms[1][0]))

    @staticmethod
    def truediv_none(terms):
        data = (terms[0][0][0] ** terms[1][0], terms[0][1][0] ** terms[1][0])
        return TrueDiv(*data).rv()


class MatMul(ArithmeticOperation):
    OPERATOR = '√'

    def __validate_terms(self, terms):
        """
        Validate root terms:
        - radicand < 0 and even index
        - index = 0
        - radicand = 0 and index < 0
        are all invalid cases where the operation is not possible

        :param terms: index and radicand
        :return: None
        """

    @staticmethod
    def string(terms):
        return Pow.string_builder()(terms)
