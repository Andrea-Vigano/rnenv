"""
Functional RNs representation test
MODULE 2

Will Implement a more restrictive interface (using @abc abstractmethod)
for the class operations implementation

Each operation must define a 'string' staticmethod (where *args is the iterable of the terms of the operation),
 an 'rv' method (which should return a RN object referencing the class as main operator and the instance operands)
 and an __init__ (where *args indicates the terms involved in the operation)
"""

from abc import abstractmethod, ABCMeta, ABC
from rnenv110.rn.mathfuncs.funcs import fraction_from_float


EC = ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']  # exponent chars


class RN:
    """
    Real Number class
    """

    def __init__(self, *args, op=None):
        if not op:
            assert len(args) == 1

        self.op = op
        self.terms = args

    def __str__(self):
        if not self.op:
            return str(self.terms[0])
        return self.op.string(*self.terms)

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
        return Pow(self, power).rv()

    def __matmul__(self, other):
        return other.__rmatmul__(self)

    def __rmatmul__(self, other):
        return MetaRoot('root_' + str(other), (Operation, ), {}, index=other)(self).rv()


class Operation(metaclass=ABCMeta):
    OPERANDS_TYPES = (RN, int)

    def __init__(self, *args):
        """

        :param args: instance operands
        """
        if not any(isinstance(term, tp) for tp in self.OPERANDS_TYPES for term in args):
            raise ValueError('Bad user operands, must be {} for {}, got a list {}'.format(
                self.OPERANDS_TYPES, self.__class__, str(list(map(lambda a: type(a), args)))
            ))
        # every item in terms is RN (not int)
        self.terms = list(map(lambda x: x if isinstance(x, RN) else RN(x), args))

    @staticmethod
    @abstractmethod
    def string(*args) -> str:
        """

        :param args: operands
        :return: string representation
        """

    def rv(self) -> RN:
        """

        :return: associated Real Number
        """

        return RN(op=self.__class__.__name__, *self.terms)


# operations example
class ArithmeticOperator(Operation, ABC):
    """
    ABC class for arithmetic operators like Add, Sub, Mul, TrueDiv and FloorDiv
    They share a similar string data handling
    """

    @classmethod
    def string_builder(cls, op):
        """
        String builder creator for Arithmetic Operators classes

        :param op: operator string
        :return: string representation
        """
        def inner(*args):
            if len(args) == 1:
                return str(args[0])
            joint = ' ' + op + ' '
            return joint.join([str(term) for term in args])
        return inner

    def rv(self):
        # terms are RN
        if not self.terms[0].op and not self.terms[1].op:
            # build func name
            code_fragment = 'self.terms[0].terms[0].' \
                            + '__' + self.__class__.__name__.lower() + '__' + '(self.terms[1].terms[0])'
            return RN(eval(code_fragment))
        return RN(op=self.__class__.__name__, *self.terms)


class Add(ArithmeticOperator):
    @staticmethod
    def string(*args) -> str:
        return Add.string_builder('+')(*args)


class Sub(ArithmeticOperator):
    @staticmethod
    def string(*args) -> str:
        return Sub.string_builder('-')(*args)


class Mul(ArithmeticOperator):
    @staticmethod
    def string(*args) -> str:
        return Sub.string_builder('*')(*args)


class TrueDiv(ArithmeticOperator):
    @staticmethod
    def string(*args) -> str:
        return Sub.string_builder('/')(*args)

    def rv(self):
        """
        Return value getter
        perform division when a is divisible by b

        :return: RN object
        """

        # terms are RN
        if not self.terms[0].op and not self.terms[1].op:
            dividend = self.terms[0].terms[0]
            divisor = self.terms[1].terms[0]
            quotient = dividend / divisor
            # perform calculation if quotient is and integer
            if round(quotient, 5) == int(quotient):
                return RN(int(quotient))
            else:
                return RN(*fraction_from_float(quotient), op=self.__class__.__name__)
        return super().rv()


class FloorDiv(ArithmeticOperator):
    @staticmethod
    def string(*args) -> str:
        return Sub.string_builder('//')(*args)


# root builder
class MetaRoot(ABCMeta):
    def __new__(mcs, name, bases, namespace, **kwargs):
        mcs.index = kwargs['index']
        assert Operation in bases
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace)

        def meta_string_builder(index):

            def inner(radicand: RN or int):
                return ''.join([EC[int(ch)] for ch in str(index)]) + '√' + str(radicand)
            return inner

        def _init(self, radicand: RN or int):
            self.radicand = radicand

        def rv(self):
            if round(self.radicand.terms[0] ** (1 / self.__class__.index), 5) == int(
                    self.radicand.terms[0] ** (1 / self.__class__.index)):
                return RN(*[int(self.radicand.terms[0] ** (1 / self.__class__.index))])
            return RN(op=self.__class__, *[self.radicand])

        # add string method (build using meta_string_builder)
        setattr(cls, 'string', staticmethod(meta_string_builder(cls.index)))
        # clear abstractmethods manually
        setattr(cls, '__abstractmethods__', frozenset())
        cls.__init__ = _init
        cls.rv = rv


class Pow(ArithmeticOperator):
    @staticmethod
    def string(*args) -> str:
        return Pow.string_builder('**')(*args)
