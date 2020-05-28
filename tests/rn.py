"""
RN class (without index parameter usage)
test
"""

import numpy as np
from rnenv110.rn.rnprops import rn_str, rn_classification


class RN:
    """
    RN class
    """
    def __init__(self, array):
        self.array = array

    @property
    def cls(self):
        return rn_classification(self.array)

    def __str__(self):
        return rn_str(self.array, self.cls)

    def __repr__(self):
        return str(self)


if __name__ == '__main__':
    # build complex number
    one = np.array([[[2, 2, 2], [3, 1, 1]], [[1, 1, 1], [0, 1, 1]]])
    two = np.array([[[1, RN(one), 2]], [[2, 1, 1]]])

    print(RN(one))
    print(RN(two))
