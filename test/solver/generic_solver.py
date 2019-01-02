import unittest
import random
import time
import numpy as np

from scipy.stats import chisquare

from src.formula import Formula, Assignment
from src.solver.utils import Falselist
from src.experiment.measurement import Measurement


class TestMeasurement(Measurement):
    def __init__(self, formula, *more_args):
        self.flips = 0
        self.begin_time = time.time()

    def count(self, flipped_var):
        self.flips += 1

    def get_run_time(self):
        return time.time() - self.begin_time


class TestDistribution(unittest.TestCase):
    def setUp(self):
        random.seed()

        cases = 10
        self.eps = 2**(-30)

        self.n = 128
        self.r = 4.2

        self.significance_level = 0.01 if __debug__ else 0.05
        self.sample_size = 1000
        self.repeat = 100
        self.max_failure = self.repeat * 0.2
        self.jump_range = self.n // 10

        self.formulae = [
            Formula.generate_satisfiable_formula(self.n,self.r)
            for _ in range(0,cases)
        ]


    def generic_test_distribution_against_heuristic(self, context_constr, heuristik, distribution):
        for f in self.formulae:
            n = f.num_vars
            assgn = Assignment.generate_random_assignment(n)
            ctx = context_constr(f,assgn)

            rejections = 0
            for r in range(0,self.repeat):
                observed_distr = np.zeros(n+1)

                # measure empirical distribution
                for _ in range(0,self.sample_size):
                    x = heuristik(ctx)
                    observed_distr[x] += 1


                # calculate expected distribution
                expected_distr = distribution(ctx)
                for i,_ in enumerate(expected_distr):
                    expected_distr[i] *= self.sample_size


                # simple length check
                self.assertEqual(len(observed_distr),len(expected_distr))


                # make buckets with at least 5 observed values in every one
                obs_buckets = [0]
                exp_buckets = [0]
                for o,e in zip(observed_distr, expected_distr):
                    obs_buckets[-1] += o
                    exp_buckets[-1] += e
                    if obs_buckets[-1] >= 5:
                        obs_buckets.append(0)
                        exp_buckets.append(0)

                #print(obs_buckets,exp_buckets,sep='\n')
                o_last = obs_buckets.pop()
                e_last = exp_buckets.pop()
                obs_buckets[-1] += o_last
                exp_buckets[-1] += e_last
                # print(obs_buckets,exp_buckets,sep='\n')

                observed_distr = np.array(obs_buckets)
                expected_distr = np.array(exp_buckets)

                self.assertEqual(len(observed_distr),len(expected_distr))

                # Chi-Square-Test

                if len(observed_distr) > 1:
                    chi_s, p_val = chisquare(observed_distr, f_exp=expected_distr, axis = None)
                    if p_val < self.significance_level:
                        rejections += 1

                else:
                    self.assertAlmostEqual(observed_distr[0], expected_distr[0], delta=self.eps)


            # go to another assignment
            for flip in random.sample(range(1,n),self.jump_range):
                ctx.update(flip)

            # print("rejections = {}".format(rejections))
            self.assertLessEqual(rejections, self.max_failure)


class TestSolver(unittest.TestCase):

    def setUp(self):
        random.seed()

        cases = 1 if __debug__ else 100

        n = 64
        r = 4.2

        formulae = [
            Formula.generate_satisfiable_formula(n,r)
            for _ in range(0,cases)
        ]

        self.solver_setup = dict(
            max_flips     = n*5,
            max_tries     = 100,
            formulae      = formulae,
            cases         = cases,
            min_successes = cases // 100,
        )


    def generic_test_solver(self, solver):
        successes = 0
        for formula in self.solver_setup['formulae']:
            assgn, measurement = solver(
                formula,
                TestMeasurement,
                self.solver_setup['max_tries'],
                self.solver_setup['max_flips'],
            )
            if assgn:
                self.assertGreater(measurement.flips, 0)
                self.assertTrue(formula.is_satisfied_by(assgn))
                successes += 1

        self.assertGreaterEqual(successes, self.solver_setup['min_successes'])


    def test_solver(self):
        pass
