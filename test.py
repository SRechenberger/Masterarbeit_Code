import unittest
import random
from src.solver.utils import Assignment

class TestAssignment(unittest.TestCase):
    def setUp(self):
        random.seed()
        self.maxDiff = None

    def test_creation(self):
        for _ in range(0,10000):
            num_vars = random.randrange(1,1001)
            assgn1 = Assignment.generate_random_assignment(num_vars)
            assgn2 = Assignment(int(str(assgn1),16),num_vars)
            self.assertEqual(str(assgn1),str(assgn2))

    def test_flip(self):
        for _ in range(0,10000):
            num_vars = random.randrange(1,1001)
            number   = random.randrange(0,pow(2,num_vars))
            assgn    = Assignment(number, num_vars)
            self.assertEqual(hex(number), str(assgn))
            to_flip  = random.randrange(1,num_vars+1)
            assgn.flip(to_flip)
            number ^= 1 << (to_flip-1)
            self.assertEqual(hex(number), str(assgn))


if __name__ == '__main__':
    unittest.main()
