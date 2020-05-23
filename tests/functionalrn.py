"""
Functional rn class concept test
"""

EC = ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']  # exponent chars


class MetaRoot(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        mcs.index = kwargs['index']
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace)

        def meta_string(_cls, radicand):
            return ''.join([EC[int(ch)] for ch in str(_cls.index)]) + '√' + str(radicand)

        def _init(self, radicand):
            self.radicand = radicand

        cls.string = classmethod(meta_string)
        cls.__init__ = _init
        cls.rv = lambda self: RN(op=self.__class__, *[self.radicand])


class Sum:
    def __init__(self, *terms):
        _terms = [0]
        for term in terms:
            if isinstance(term, int):
                _terms[0] += term
            elif isinstance(term, RN):
                if not term.op:
                    _terms[0] += term.terms[0]
            else:
                _terms.append(term)
        self.terms = _terms

    @staticmethod
    def string(terms):
        return ' + '.join(map(lambda x: str(x), terms))

    def rv(self):
        return RN(op=Sum, *self.terms)


class RN:
    """
    Functional RN class,

    A real number is defined by one or more integers, and an operator function that should
    take those integers as parameters, but it may not be able to return a single value, so
    it may not be performed as an operation and carried as it is.

    For example:

    To represent a sum of numbers, an RN should look like this

    2 + 4 -> RN(sum, 2, 4)

    This form is actually embedded in every operation-magic-methods, so that when you
    perform:

    2 + 4, the value returned is actually RN(sum, 2, 4)

    In this case the number would have been compacted down to 6, but in some cases it may not,
    for example:

    √2 -> RN(sqr, 2)

    cannot be reduced any more than this. This is not a fixed state by the way, as if you were
    to elevate that number by 2, it should be able to recognise the pattern and return a 2.

    Defined operators:
    Arithmetic operators: add, sub, mul, div, floordiv, mod, pow (with exp choice), root (with index choice)
    Goniometrical operators: sin, cos, tan, cot, scs, sec, arccos, arcsin, arctan, arccot
    Exponential operators: exp (with base choice), log (with base choice), ln
    More to come...
    """

    def __init__(self, *terms, op=None):
        """
        Where op is the operator to which the terms are parameters, if None (as default)
        no operation is passed ad terms are taken as they are.

        :param op: Operator
        :param terms: Terms (operator parameter)
        """

        if not op:
            assert len(terms) == 1

        # assign parameters
        self.op = op
        self.terms = terms

    # representation methods
    def __str__(self):
        if not self.op:
            return str(self.terms[0])
        return self.op.string(self.terms)

    def __repr__(self):
        pass

    # operations
    def _are_compatible(self, other):
        pass

    def __add__(self, other):
        return Sum(self, other).rv()

    def __sub__(self, other):
        pass

    def __matmul__(self, other):
        return _root(self)(other)

    def __rmatmul__(self, other):
        return _root(other)(self)

