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


from abc import ABCMeta, abstractmethod, ABC
from math import gcd
from fractions import Fraction


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
            return str(self.terms[0])
        return self.op.string(self.terms)

    def __repr__(self):
        return str(self)

    # data casing
    def __int__(self):
        # TODO re write int code
        if not self.op:
            return int(self.terms[0])
        return NotImplemented

    # operations
    # Arithmetic operations: add, sub, mul, truediv, floordiv, pow, root (using matmul for that)

    # op validator (used to assert that other is always an RN, even if integers are also accepted)
    @staticmethod
    def __validate(func):
        def inner(self: RN, other: RN or int) -> RN:
            # self is already RN
            if not (isinstance(other, RN) or isinstance(other, int)):
                raise ValueError('Unable to perform {} between {} (RN) and {} ({})'
                                 .format(func, self, other, type(other)))
            if isinstance(other, int):
                other = RN(other)
            return func(self, other)
        return inner

    def __add__(self, other):
        return Add(self, other).rv()

    def __sub__(self, other):
        return Sub(self, other).rv()

    def __mul__(self, other):
        return Mul(self, other).rv()

    def __truediv__(self, other):
        return TrueDiv(self, other).rv()

    def __floordiv__(self, other):
        return FloorDiv(self, other).rv()

    def __pow__(self, power, modulo=None):
        pass

    def __matmul__(self, other):
        pass


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

        :return: RN object
        """

        # standard return value
        return RN(op=self.__class__, *self.terms)


# Arithmetic operations
# -> Add, Sub, Mul, TrueDiv, FloorDiv (excluding Pow and Root)
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
            - TODO if one or both ops is TrueDiv -> fractions algebra

        if operation cannot be performed, return Operation rv method call

        :return: RN object
        """

        # no op case
        if not self.terms[0].op and not self.terms[1].op:
            # build code fragment
            code_fragment = 'self.terms[0].terms[0].' \
                            + '__' + self.__class__.__name__.lower() + '__' + '(self.terms[1].terms[0])'
            return RN(eval(code_fragment))

        # TrueDiv - no op ## no op - TrueDiv ## TrueDiv - TrueDiv
        if self.terms[0].op == TrueDiv or self.terms[1].op == TrueDiv:
            if self.terms[0].op == TrueDiv:
                term_1 = Fraction(*self.terms[0].terms.__int__())
            elif not self.terms[0].op:
                term_1 = Fraction(self.terms[0].terms[0].__int__(), 1)
            if self.terms[1].op == TrueDiv:
                # fraction operation
                term_2 = Fraction(*self.terms[1].terms.__int__())
            elif not self.terms[1].op:
                term_2 = Fraction(self.terms[1].terms[0].__int__(), 1)
            try:
                # build code fragment
                code_fragment = 'term_1.' \
                                + '__' + self.__class__.__name__.lower() + '__' + '(term_2)'
                data = eval(code_fragment)
                return RN(data.numerator, data.denomiator)
            except NameError:
                # if terms have not been defined
                pass
        return super().rv()


class Add(ArithmeticOperation):

    OPERATOR = '+'

    @staticmethod
    def string(terms):
        return Add.string_builder()(terms)


class Sub(ArithmeticOperation):
    OPERATOR = '-'

    @staticmethod
    def string(terms):
        return Sub.string_builder()(terms)


class Mul(ArithmeticOperation):
    OPERATOR = '*'

    @staticmethod
    def string(terms):
        return Mul.string_builder()(terms)


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

    def rv(self):
        """
        Custom rv for TrueDiv operation:
        - Treat as fraction, reduce num and den to prime terms

        :return: RN object
        """

        if not self.terms[0].op and not self.terms[1].op:
            dividend = self.terms[0].terms[0]
            divisor = self.terms[1].terms[0]
            _gcd = gcd(dividend, divisor)
            if _gcd != 1:
                data = (dividend // _gcd, divisor // _gcd)
                if data[1] == 1:
                    # exact division -> operation fully performed
                    return RN(data[0])
                return RN(op=self.__class__, *data)
            return RN(op=self.__class__, *self.terms)
        return super().rv()


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
