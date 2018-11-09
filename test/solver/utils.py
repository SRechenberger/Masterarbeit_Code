import unittest
import random
import os

from src.formula import Formula, Assignment
from src.solver.utils import Falselist, Scores, DiffScores
from src.experiment.utils import FormulaSupply


class TestFalselist(unittest.TestCase):
    def setUp(self):
        random.seed()
        self.maxDiff = None


    def test_add(self):
        l = Falselist()
        t = set()
        xs = list(range(1,1000))
        random.shuffle(xs)
        for x in xs:
            l.add(x)
            t.add(x)
            self.assertEqual(set(l.lst),t)


    def test_remove(self):
        l = Falselist()
        xs = list(range(1,1000))
        random.shuffle(xs)
        for x in xs:
            l.add(x)
        for x in random.sample(xs, 100):
            l.remove(x)
        for k,v in l.mapping.items():
            self.assertEqual(k, l.lst[v])


class TestScores(unittest.TestCase):
    def setUp(self):
        random.seed()
        dirname = 'test_files'
        Formula.generate_formula_pool(
            dirname,
            5,
            256,
            4.2,
            poolsize=3,
        )
        self.paths = random.sample(
            list(
                map(
                    lambda fname: os.path.join(dirname, fname),
                    filter(
                        lambda fname: fname.endswith('.cnf'),
                        os.listdir(dirname)
                    )
                )
            ),
            10
        )
        self.buffsize = 5


    def test_diff_score(self):
        for _, formula in FormulaSupply(self.paths, self.buffsize):
            n = formula.num_vars
            assgn = Assignment.generate_random_assignment(n)
            falselist = Falselist()
            diff_score = DiffScores(formula,assgn,falselist)

            self.assertTrue(diff_score.self_test(formula, assgn, falselist))

            to_flips = [
                i
                for _ in range(0,10)
                for i in random.sample(range(1,n+1), n // 10)
            ]

            for to_flip in to_flips:
                diff_score.flip(to_flip, formula, assgn, falselist)

            self.assertTrue(diff_score.self_test(formula, assgn, falselist))

    # @unittest.skip("takes too long")
    def test_score(self):
        for _, formula in FormulaSupply(self.paths, self.buffsize):
            n = formula.num_vars
            falselist = Falselist()
            assgn = Assignment.generate_random_assignment(n)

            per_side = 5
            to_flips = random.sample(range(1,n+1), per_side * 2)
            pos_flips = to_flips[0:per_side]
            neg_flips = to_flips[per_side:]

            for pos in pos_flips:
                assgn[pos-1] = True

            for neg in neg_flips:
                assgn[neg-1] = False

            scores = Scores(formula, assgn, falselist)

            # first check after creation
            self.assertTrue(scores.self_test(formula, assgn, falselist))

            to_flips = [
                i
                for _ in range(0,10)
                for i in random.sample(range(1,n+1), max(1,n // 100))
            ]

            for to_flip in to_flips:
                scores.flip(to_flip, formula, assgn, falselist)

                self.assertTrue(scores.self_test(formula, assgn, falselist))

