from src.solver.utils import Formula
from src.experiment.utils import FormulaSupply, binomial_vec, Queue
import unittest
import random
import os
from functools import partial

class TestHelperFunctions(unittest.TestCase):
    def setUp(self):
        random.seed()

    def test_binomial_vec(self):
        for i in range(1,1000):
            self.assertTrue(abs(sum(binomial_vec(i)) - 1) < 0.001)

class TestQueue(unittest.TestCase):
    def setUp(self):
        random.seed()
        self.cases = 100

    def test_push_read(self):
        for _ in range(0, self.cases):
            size = random.randrange(0,1000) + 1

            test_queue = Queue(size)

            xs = random.sample(range(1,1001), size)

            for x in xs:
                test_queue.push(x)

            ys = []
            while not test_queue.is_empty():
                ys.append(test_queue.pop())

            self.assertEqual(xs,ys)


    def test_over_fill(self):
        for _ in range(0, self.cases):
            size = random.randrange(0,1000) + 1

            test_queue = Queue(size)

            xs = random.sample(range(1,1001), size)
            ys = random.sample(range(1,1001), size)

            for x in xs:
                test_queue.push(x)

            zs = []
            for y in ys:
                zs.append(test_queue.push(y))

            self.assertEqual(xs,zs)





