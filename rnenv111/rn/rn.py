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
# TODO implement root reduction algorithms
# TODO update string build for RN class (maybe with operation priority implementation)


from abc import ABCMeta, abstractmethod, ABC
from numpy import lcm
import math
from rnenv111.rn.mathfuncs.funcs import reduce_fraction, reduce_root


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
        executing the operations related to self and each term of self

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
            if func == '__matmul__':
                return flt_terms[0] ** (1 / flt_terms[1])
            else:
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

    # equality
    @_validate
    def __eq__(self, other):
        """
        self == other

        Comparison is made by comparing float values of self and other

        :param other: RN or int
        :return: Boolean
        """

        if float(self) == float(other):
            return True
        return False

    @_validate
    def __ne__(self, other):
        """
        self != other

        :param other: RN or int
        :return: Boolean
        """

        return not self == other

    # comparisons
    @_validate
    def __gt__(self, other):
        """
        self > other

        Compare float values

        :param other: RN or int
        :return: Boolean
        """

        return float(self) > float(other)

    @_validate
    def __ge__(self, other):
        """
        self >= other

        Compare float values

        :param other: RN or int
        :return: Boolean
        """

        return float(self) >= float(other)

    @_validate
    def __lt__(self, other):
        """
        self < other

        Compare float values

        :param other: RN or int
        :return: Boolean
        """

        return float(self) < float(other)

    @_validate
    def __le__(self, other):
        """
        self <= other

        Compare float values

        :param other: RN or int
        :return: Boolean
        """

        return float(self) <= float(other)

    # types getters
    # TODO define actual logic for is_rational / is_irrational
    def is_integer(self):
        return not self.op

    def is_rational(self):
        return True

    def is_irrational(self):
        return False

    # operations
    # Arithmetic operations: add, sub, mul, truediv, floordiv, pow, root (using matmul for that) (binary operators)
    # + neg, pos and abs (unary operators)

    # when the arguments make it to the actual function, they will always be RNs, as the decorator
    # __validate will convert them if any integer is found

    def __neg__(self):
        return self * -1

    def __pos__(self):
        return self

    def __abs__(self):
        return self if self >= 0 else -self

    @_validate
    def __add__(self, other):
        """
        self + other

        :param other: RN (if int is turned to RN by __validate)
        :return: RN object sum
        """

        return Add(self, other).rv()

    @_validate
    def __radd__(self, other):
        return Add(other, self).rv()

    @_validate
    def __sub__(self, other):
        """
        self - other

        :param other: RN (if int is turned to RN by __validate)
        :return: RN object difference
        """

        return Sub(self, other).rv()

    @_validate
    def __rsub__(self, other):
        return Sub(other, self).rv()

    @_validate
    def __mul__(self, other):
        """
        self * other

        :param other: RN (if int is turned to RN by __validate)
        :return: RN object product
        """

        return Mul(self, other).rv()

    @_validate
    def __rmul__(self, other):
        return Mul(other, self).rv()

    @_validate
    def __truediv__(self, other):
        """
        self / other

        Validate: raise error if other == 0

        :param other: RN (if int is turned to RN by __validate)
        :return: RN object quotient
        """

        return TrueDiv(self, other).rv()

    @_validate
    def __rtruediv__(self, other):
        return TrueDiv(other, self).rv()

    @_validate
    def __floordiv__(self, other):
        """
        self // other

        Validate: raise error if other == 0

        :param other: RN (if int is turned to RN by __validate)
        :return: RN object exact quotient
        """

        return FloorDiv(self, other).rv()

    @_validate
    def __rfloordiv__(self, other):
        return FloorDiv(other, self).rv()

    @_validate
    def __mod__(self, other):
        """
        self % other

        Get by calculating self / other - self // other

        :param other:
        :return:
        """

        return Mod(self, other).rv()

    @_validate
    def __rmod__(self, other):
        return Mod(other, self).rv()

    @_validate
    def __pow__(self, power, modulo=None):
        """
        self ** power

        Validate: raise error if self and power are both zeros
                              if self < 0 and power is not rational

        :param power: RN power
        :param modulo: None
        :return: RN object power
        """
        return Pow(self, power).rv()

    @_validate
    def __rpow__(self, other, modulo=None):
        return Pow(other, self).rv()

    @_validate
    def __matmul__(self, other):
        """
        self@ other
        Which is interpreted as [self]√ other

        Validate: raise error if self is even and other < 0
                              if self is zero
                              if self < 0 and other is zero

        :param other: Radicand
        :return: RN object root
        """
        return MatMul(self, other).rv()

    @_validate
    def __rmatmul__(self, other):
        return MatMul(other, self).rv()


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
    # operand properties
    PROPERTIES = NotImplemented

    def __init__(self, *terms):
        """
        Standard initialization of the operation:
        validate terms -> self.validate_terms
        set terms attribute, parsing every item so that there are only RN in the list

        :param terms: operation terms, their number vary depending on the operation performed
        """

        self._validate_terms(terms)
        self.terms = tuple(map(lambda x: x if isinstance(x, RN) else RN(x), terms))

    def _validate_terms(self, terms):
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
    PROPERTIES = []

    def _validate_terms(self, terms):
        super()._validate_terms(terms)

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
        op_1 = self.terms[0].op
        op_2 = self.terms[1].op
        op_1 = op_1.__name__.lower() if op_1 else 'none'
        op_2 = op_2.__name__.lower() if op_2 else 'none'
        try:
            # try to call the operation method for the terms defined operations
            return eval('self.' + op_1 + '_' + op_2 + '(*self.terms)')
        except AttributeError:
            # no operation method found
            # -> if commutative properties
            if 'commutative' in self.PROPERTIES:
                try:
                    func = eval('self.' + op_2 + '_' + op_1)
                    return eval('self.' + op_2 + '_' + op_1 + '(*reversed(self.terms))')
                except AttributeError:
                    pass
            return super().rv()


# possible data parsing in operation:
# - Complexity level add (no operation)
# - Nested add / sub parsing
# - Fractional operations
# - Addends merge into mul

def _complexity_level_add(a, b):
    """
    Std operation parsing procedure,
    used for Add operations that cannot
    be reduced, so the complexity level is increased

    :param a: First RN
    :param b: Second RN
    :return: RN sum object
    """

    # No validation needed, as this method is only called locally
    data = (a, b)
    return RN(op=Add, *data)


def _sum_sub_parsing(_a: bool, _b: bool):
    """
    Operation parsing involving sums or subs,
    will parse the terms involved in the actual operation
    and try merge them.

    Will have to specify where both the operands are sum / sub or only one.

    :param _a: First RN
    :param _b: Second RN
    :return: RN object
    """

    def inner(a, b):
        """
        -> sum data parsing
            list every term in the sum (considering that sum may involve more than one term)
            - loop sum terms, if term is a sum -> parse, else add to list
            if any of the terms in list is compatible to the int, add it
            Re build new sum object if merging has been done

        Compatibility check:
        if a + term is not a sum, merge

        Example:
        3 + (√3 + 4) --> list = [Root 3, 4] where for is compatible with 3 (both integer)
        -> √3 + 7
        """
        terms = []
        terms += Add._parse_sum(a) if _a else [a]
        terms += Add._parse_sum(b) if _b else [b]
        return Add._sum_terms(Add._merge_sum(terms))

    return inner


def _fractional_sum(_a: bool, _b: bool):
    """
    Operation involving fractions (TrueDiv objects)

    Will bring everything on a single fraction and sum the terms
    there.

    Need to specify which operands are fractions

    :param _a: First RN
    :param _b: Second RN
    :return: RN object
    """

    def inner(a, b):
        # hardcoded logic
        if not _b:
            return TrueDiv(a[0] + b * a[1], a[1]).rv()
        if not _a:
            return TrueDiv(b[0] + a * b[1], b[1]).rv()
        else:
            return TrueDiv(a[0] * b[1] + a[1] * b[0], a[1] * b[1]).rv()

    return inner


def _addends_merge(a, b):
    """
    Operation involving two equal addends
    that are turned into a Mul object

    :param a: First RN
    :param b: Second RN
    :return: RN mul object
    """

    if a == b:
        data = (2, a)
        return RN(op=Mul, *data)
    data = (a, b)
    return RN(op=Add, *data)


class Add(ArithmeticOperation):

    OPERATOR = '+'
    PROPERTIES = ['commutative']

    @staticmethod
    def string(terms):
        return Add.string_builder()(terms)

    @staticmethod
    def _parse_sum(_sum):
        """
        Returns the list of terms involved in the sum / sub

        :param _sum: RN sum / sub
        :return: terms list
        """
        _list = []

        # get sum / sub terms
        for p, term in enumerate(_sum.terms):
            if term.op in (Add, Sub):
                _list.extend(Add._parse_sum(term))
            else:
                if _sum.op == Sub and p == 1:
                    _list.append(-term)
                else:
                    _list.append(term)
        return _list

    @staticmethod
    def _merge_sum(terms):
        """
        Returns the parsed terms of the sum / sub,
        merging the terms that can be merged

        :param terms: sum / sub terms (use Add._parse_sum to get them)
        :return: terms list (parsed)
        """

        # sort by op class name (if terms can be merged, they have the same op)
        terms = sorted(terms, key=lambda x: x.op.__name__.lower() if x.op else 'none')
        for p, term in enumerate(terms):
            try:
                _sum = term + terms[p + 1]
                if _sum.op != Add:
                    terms[p] = None
                    terms[p + 1] = _sum
            except IndexError:
                continue
        return [term for term in terms if term]

    @staticmethod
    def _sum_terms(terms):
        """
        Sum up parsed sum terms

        :param terms: Addends
        :return: RN object sum
        """

        if len(terms) == 0:
            return RN(0)
        elif len(terms) == 1:
            return terms[0]
        rv = 0
        for p, term in enumerate(terms):
            if p == 0:
                rv = term + terms[1]
            elif p != 1:
                rv += term
        return rv

    # operations explicit declarations
    @staticmethod
    def none_none(a, b):
        """
        Int + Int

        Simple integers sum

        :return: RN object
        """

        return RN(a[0] + b[0])

    none_add = staticmethod(_sum_sub_parsing(False, True))
    none_sub = staticmethod(_sum_sub_parsing(False, True))
    none_mul = staticmethod(_complexity_level_add)
    none_truediv = staticmethod(_fractional_sum(True, False))
    none_floordiv = staticmethod(_complexity_level_add)
    none_mod = staticmethod(_complexity_level_add)
    none_pow = staticmethod(_complexity_level_add)
    none_matmul = staticmethod(_complexity_level_add)
    add_add = staticmethod(_sum_sub_parsing(False, True))
    add_sub = staticmethod(_sum_sub_parsing(False, True))
    add_mul = staticmethod(_complexity_level_add)

    @staticmethod
    def add_truediv(a, b):
        """
        Sum + fraction

        bring every think to single fraction,
        then sum numerator terms

        num = each term of sum * den + num

        :return: RN object
        """

        terms = Add._parse_sum(a * b[1]) + [b[0]]
        # sum num terms and return fraction
        return TrueDiv(Add._sum_terms(terms), a[1]).rv()

    add_floordiv = staticmethod(_complexity_level_add)
    add_mod = staticmethod(_complexity_level_add)
    add_pow = staticmethod(_complexity_level_add)
    add_matmul = staticmethod(_sum_sub_parsing(False, True))
    sub_sub = staticmethod(_sum_sub_parsing(False, True))
    sub_mul = staticmethod(_complexity_level_add)
    sub_truediv = staticmethod(_fractional_sum(True, False))
    sub_floordiv = staticmethod(_complexity_level_add)
    sub_mod = staticmethod(_complexity_level_add)
    sub_pow = staticmethod(_complexity_level_add)
    sub_matmul = staticmethod(_sum_sub_parsing(False, True))
    mul_mul = staticmethod(_complexity_level_add)
    mul_truediv = staticmethod(_fractional_sum(True, False))
    mul_floordiv = staticmethod(_complexity_level_add)
    mul_pow = staticmethod(_complexity_level_add)

    @staticmethod
    def mul_matmul(a, b):
        """
        Mul + Root

        if one of the terms in Mul is equal to Root,
        merge

        :return: RN object
        """

        data = (a, b)
        if a[0] == b and not a[1].op:
            data = (a[1] + 1, b)
        elif a[1] == b and not a[0].op:
            data = (a[0] + 1, b)
        if data[0].op == Add:
            data = (a, b)
        return RN(op=Add, *data)

    truediv_truediv = staticmethod(_fractional_sum(True, False))
    truediv_floordiv = staticmethod(_fractional_sum(True, False))
    truediv_mod = staticmethod(_fractional_sum(True, False))
    truediv_pow = staticmethod(_fractional_sum(True, False))
    truediv_matmul = staticmethod(_fractional_sum(True, False))
    floordiv_floordiv = staticmethod(_addends_merge)
    floordiv_mod = staticmethod(_complexity_level_add)
    floordiv_pow = staticmethod(_complexity_level_add)
    floordiv_matmul = staticmethod(_complexity_level_add)
    mod_mod = staticmethod(_addends_merge)
    mod_pow = staticmethod(_complexity_level_add)
    mod_matmul = staticmethod(_complexity_level_add)
    pow_pow = staticmethod(_addends_merge)
    pow_matmul = staticmethod(_complexity_level_add)
    matmul_matmul = staticmethod(_addends_merge)


class Sub(ArithmeticOperation):
    OPERATOR = '-'

    @staticmethod
    def string(terms):
        return Sub.string_builder()(terms)

    # operations explicit declarations

    @staticmethod
    def none_none(a, b):
        return RN(a[0] - b[0])

    @staticmethod
    def truediv_none(a, b):
        """
        fraction - integer:
        - num - integer * den / den

        :return: RN object
        """

        data = (a[0] - b[0] * a[1], a[1])
        return TrueDiv(*data).rv()

    @staticmethod
    def none_truediv(a, b):
        """
        integer - fraction:
        - integer * den - num / den

        :return: RN object
        """

        data = (a[0] * b[1] - b[0], b[1])
        return TrueDiv(*data).rv()

    @staticmethod
    def truediv_truediv(a, b):
        """
        fraction + fraction
        - num1 * den2 - num2 * den1, den1 * den2

        :return: RN object
        """

        data = (a[0] * b[1] - b[0] * a[1], a[1] * b[1])
        return TrueDiv(*data).rv()

    @staticmethod
    def matmul_matmul(a, b):
        """
        Root - Root

        Reduce if a == b

        :return: RN object
        """

        if a == b:
            return RN(0)
        data = (a, b)
        return RN(op=Add, *data)


class Mul(ArithmeticOperation):
    OPERATOR = '*'
    PROPERTIES = ['commutative']

    @staticmethod
    def string(terms):
        return Mul.string_builder()(terms)

    @staticmethod
    def none_none(a, b):
        return RN(a[0] * b[0])

    @staticmethod
    def truediv_none(a, b):
        """
        fraction * integer:
        - num * integer, den
        - reduce integer and den if possible

        :return: RN object
        """

        data = (a[0] * b[0], a[1])
        return TrueDiv(*data).rv()

    @staticmethod
    def none_truediv(a, b):
        return Mul.truediv_none(b, a)

    @staticmethod
    def truediv_truediv(a, b):
        """
        fraction * fraction:
        - num1 * num2, den1 * den2

        :return: RN object
        """

        data = (a[0] * b[0], a[1] * b[1])
        return TrueDiv(*data).rv()

    @staticmethod
    def matmul_matmul(a, b):
        """
        Root * Root

        get indexes lcm, result is a new root,
        with index equal to the lcm, and the radicand
        equal to the product of each radicand ** (lcm // old index)

        :return: RN object
        """

        _lcm = int(lcm(a[0], b[0]))
        return MatMul(_lcm, (a[1] ** (_lcm // a[0])) * (b[1] ** (_lcm // b[0]))).rv()


class TrueDiv(ArithmeticOperation):
    OPERATOR = '/'

    def _validate_terms(self, terms):
        """
        Override validation method
        - check that den is not 0

        :param terms:
        :return:
        """
        super()._validate_terms(terms)
        if terms[1] == 0:
            raise ZeroDivisionError('Bad user argument, cannot divide by zero')

    @staticmethod
    def string(terms):
        return TrueDiv.string_builder()(terms)

    @staticmethod
    def none_none(a, b):
        """
        No op case: check if division can be performed completely, partially or not

        :return: RN object
        """
        num, den = reduce_fraction(a[0], b[0])
        if den == 1:
            return RN(num)
        data = (RN(num), RN(den))
        return RN(op=TrueDiv, *data)

    @staticmethod
    def truediv_none(a, b):
        """
        fraction / integer

        :return: RN object
        """

        data = (a[0], a[1] * b[0])
        return TrueDiv(*data).rv()

    @staticmethod
    def none_truediv(a, b):
        """
        integer / fraction

        :return: RN object
        """

        data = (a[0] * b[1], b[0])
        return TrueDiv(*data).rv()

    @staticmethod
    def truediv_truediv(a, b):
        """
        fraction / fraction

        :return: RN object
        """

        data = (a[0] * b[1], a[1] * b[0])
        return TrueDiv(*data).rv()


class FloorDiv(ArithmeticOperation):
    OPERATOR = '//'

    def _validate_terms(self, terms):
        """
        Override validation method
        - check that den is not 0

        :param terms:
        :return:
        """
        super()._validate_terms(terms)
        if terms[1] == 0:
            raise ZeroDivisionError('Bad user argument, cannot divide by zero')

    @staticmethod
    def string(terms):
        return FloorDiv.string_builder()(terms)

    @staticmethod
    def none_none(a, b):
        return RN(a[0] // b[0])

    @staticmethod
    def truediv_none(a, b):
        """
        fraction // integer

        :return: RN object
        """

        data = (float(a) // b[0], )
        return RN(*data)

    @staticmethod
    def none_truediv(a, b):
        """
        integer // fraction

        :return: RN object
        """

        data = (a[0] // float(b), )
        return RN(*data)

    @staticmethod
    def truediv_truediv(a, b):
        """
        fraction // fraction

        :return: RN object
        """

        data = (float(a) // float(b), )
        return RN(*data)


class Mod(ArithmeticOperation):
    OPERATOR = '%'

    def _validate_terms(self, terms):
        """
        Validate mod terms:
        - other != 0

        :param terms: operation terms
        :return: None
        """

        super()._validate_terms(terms)
        if terms[1] == 0:
            raise ValueError('Unable to operate {} with {} and zero'
                             .format(self.__class__.__name__, terms[0]))

    @staticmethod
    def string(terms):
        return Mod.string_builder()(terms)

    @staticmethod
    def none_none(a, b):
        """
        Integer % Integer

        :return: RN object mod
        """

        return a[0] % b[0]


class Pow(ArithmeticOperation):
    OPERATOR = '**'

    def __init__(self, *terms):
        """
        Initialize Pow object, if exponent is negative,
        change its value to positive and change base to 1 / base

        :param terms: Pow terms
        """

        super().__init__(*terms)
        if self.terms[1] < 0:
            self.terms = (1 / self.terms[0], -self.terms[1])

    def _validate_terms(self, terms):
        """
        Validate pow terms:
        - exponent = 0 and base = 0
        - real exponent and base < 0
        are all cases where it is no possible to perform the operation

        :param terms: base and exponent
        :return: None
        """

        super()._validate_terms(terms)
        if terms[0] == 0 and terms[1] == 0:
            raise ValueError('Unable to perform 0^0')
        elif terms[0] < 0 and not terms[1].is_rational:
            raise ValueError('Unable to calculate operation {} with negative base {} and real exponent {}'
                             .format(self.__class__.__name__, terms[0], terms[1]))

    @staticmethod
    def string(terms):
        return Pow.string_builder()(terms)

    @staticmethod
    def none_none(a, b):
        """
        Integer ** Integer

        :return: RN object
        """

        return RN(a[0] ** b[0])

    @staticmethod
    def truediv_none(a, b):
        """
        fraction ** Integer

        :return: RN object
        """

        data = (a[0] ** b[0], a[1] ** b[0])
        return TrueDiv(*data).rv()

    @staticmethod
    def none_truediv(a, b):
        """
        Integer ** (num / den)

        -> [den] Root (Integer ** num)

        :return: RN object
        """

        data = (b[1], a[0] ** b[0])
        return MatMul(*data).rv()

    @staticmethod
    def truediv_truediv(a, b):
        """
        fraction ** fraction

        -> Root(den_2, fraction_1 ** num_2)

        :return: RN object
        """

        return Pow.none_truediv(a, b)

    @staticmethod
    def matmul_none(a, b):
        """
        Root ** Integer

        -> [Index]√ (Radicand ** Integer)

        :return: RN object
        """

        return MatMul(a[0], a[1] ** b).rv()

    @staticmethod
    def matmul_truediv(a, b):
        """
        Root ** fraction

        -> [Index]√ (Radicand ** Integer)

        :return: RN object
        """

        return Pow.matmul_none(a, b)


class MatMul(ArithmeticOperation):
    OPERATOR = '√'

    def _validate_terms(self, terms):
        """
        Validate root terms:
        - radicand < 0 and even index
        - index = 0
        - radicand = 0 and index < 0
        are all invalid cases where the operation is not possible

        :param terms: index and radicand
        :return: None
        """

        super()._validate_terms(terms)
        if terms[0] % 2 == 0 and terms[1] < 0:
            raise ValueError('Unable to perform {} of even index {} and negative radicand {}'
                             .format(self.__class__.__name__, terms[0], terms[1]))
        elif terms[0] == 0:
            raise ValueError('Unable to perform {} of zero index and radicand {}'
                             .format(self.__class__.__name__, terms[1]))
        elif terms[0] < 0 and terms[1] == 0:
            raise ValueError('Unable to perform {} of negative index {} and zero radicand'
                             .format(self.__class__.__name__, terms[0]))

    @staticmethod
    def string(terms):
        return MatMul.string_builder()(terms)

    @staticmethod
    def none_none(a, b):
        """
        [Integer]√ Integer

        Save sign
        Check if root is an integer -> return simple RN
        else -> return RN with op = Root

        :param a: RN index
        :param b: RN radicand
        :return: RN object root
        """

        radicand, index, sign = b[0], a[0], False
        if b < 0:
            radicand = -radicand
            sign = True
        root = radicand ** (1 / index)
        if int(root) == round(root, 5):
            return RN(int(root)) if not sign else RN(-int(root))
        else:
            # reduce root
            mul_factor, index, radicand = reduce_root(index, radicand)
            data = (index, radicand)
            if mul_factor != 1:
                data = (mul_factor, RN(op=MatMul, *data))
                return RN(op=Mul, *data)
            return RN(op=MatMul, *data)

    @staticmethod
    def none_truediv(a, b):
        """
        [Integer]√ fraction

        Integer root of both
        then try rationalization
        # TODO implement rationalization

        :return: RN object
        """

        data = (MatMul(a, b[0]).rv(), MatMul(a, b[1]).rv())
        return RN(op=TrueDiv, *data)

    @staticmethod
    def truediv_none(a, b):
        """
        [fraction]√ Integer

        Use Integer root of base ** denominator

        :return: RN object
        """

        return MatMul(a[0], Pow(b, a[1]).rv()).rv()

    @staticmethod
    def truediv_truediv(a, b):
        """
        [fraction]√ fraction

        Same code of truediv_none

        :return: RN object
        """

        return MatMul.truediv_none(a, b)

    @staticmethod
    def none_matmul(a, b):
        """
        [Integer]√ Root

        New index is product of old indexes

        :return: RN object
        """

        data = (a * b[0], b[1])
        return RN(op=MatMul, *data)

    @staticmethod
    def truediv_matmul(a, b):
        """
        [fraction]√ Root

        New index is product of old indexes,
        parse as MatMul after

        :return: RN object
        """

        return MatMul(a * b[0], b[1]).rv()
