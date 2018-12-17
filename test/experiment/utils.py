import unittest
import random
import os
import math

from functools import partial

from src.solver.utils import Formula
from src.experiment.utils import FormulaSupply, Queue, WindowEntropy, entropy, mutual_information
from src.analysis.utils import binomial_vec

from scipy.stats import binom

class TestHelperFunctions(unittest.TestCase):
    def setUp(self):
        random.seed()
        self.eps = 2**(-30)

    def test_binomial_vec(self):
        for i in range(1,1000):
            self.assertAlmostEqual(sum(binomial_vec(i)), 1, delta=self.eps)


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


class TestWindowEntropy(unittest.TestCase):

    def setUp(self):
        random.seed()
        self.cases = 100
        self.eps = 2**(-30)


    def test_max_entropy(self):
        xs = list(range(0,1000))
        for _ in range(0,self.cases):
            window = WindowEntropy(1000)
            random.shuffle(xs)
            for x in xs:
                window.count(x)
            self.assertAlmostEqual(window.get_entropy(), math.log(1000,2), delta=self.eps)


    def test_min_entropy(self):
        xs = [1 for _ in range(0,1000)]
        for _ in range(0,self.cases):
            window = WindowEntropy(1000)
            for x in xs:
                window.count(x)
            self.assertEqual(window.get_entropy(), 0)
            for x in xs:
                window.count(x)
            self.assertEqual(window.get_entropy(), 0)


    def test_entropy(self):
        for _ in range(0,self.cases):
            sequence = [
                random.randrange(0,100)
                for _ in range(0,1000)
            ]
            window = WindowEntropy(1000)
            dist = {}
            for x in sequence:
                if x in dist:
                    dist[x] += 1
                else:
                    dist[x] = 1
                window.count(x)
            h_observed = window.get_entropy()
            h_expected = entropy(dist)
            self.assertAlmostEqual(h_observed, h_expected, delta=self.eps)

    def test_mutual_information(self):
        for _ in range(0,self.cases):
            sequence = [
                random.randrange(0,100)
                for _ in range(0,1000)
            ]
            sequence = list(zip(sequence, sequence[1:]))
            window_X = WindowEntropy(999)
            window_Y = WindowEntropy(999)
            window_XY = WindowEntropy(999)

            dist = {}

            for (x,y) in sequence:
                window_X.count(x)
                window_Y.count(y)
                window_XY.count((x,y))

                if (x,y) in dist:
                    dist[x,y] += 1
                else:
                    dist[x,y] = 1

            i_observed = window_X.get_entropy() + window_Y.get_entropy() - window_XY.get_entropy()
            i_expected = mutual_information(dist)
            self.assertAlmostEqual(i_observed, i_expected, delta=self.eps)
