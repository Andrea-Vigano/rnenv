import unittest
from rnenv111.rn.rn import RN


class RNTestCase(unittest.TestCase):
    def test_arithmetic_operations(self):
        # will test arithmetic operators with some rational expression
        self.assertEqual(((RN(7) * (RN(2) + RN(1)) - RN(2) * RN(3)) / (RN(1) + RN(2))) - ((RN(3) * RN(2)) - RN(5)), 4)
        self.assertEqual(RN(63) - (RN(48) - (RN(14) + RN(2) * RN(16))) * (RN(2) * RN(12)) -
                         (RN(2) + RN(28) / RN(4)) - RN(18) / (RN(14) - RN(48) / RN(24) - RN(56) / RN(8) - RN(2)), 0)


if __name__ == '__main__':
    unittest.main()
