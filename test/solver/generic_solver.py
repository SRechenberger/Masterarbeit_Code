import unittest
import random
import time
import numpy as np

from src.formula import Formula, Assignment
from src.solver.utils import Falselist
from src.experiment.measurement import Measurement

from scipy.stats import chisquare


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
        n = 128
        r = 4.2

        self.significance_level = 0.05
        self.sample_size = 100
        self.repeat = 10 if __debug__ else 100
        self.max_failure = self.repeat * 0.1
        self.jump_range = n // 10

        self.formulae = [
            Formula.generate_satisfiable_formula(n,r)
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
                    observed_distr[x] += 1/self.sample_size

                self.assertTrue(abs(sum(observed_distr) - 1) < 0.00001)

                # calculate expected distribution
                expected_distr = distribution(ctx)

                # simple length check
                self.assertEqual(len(observed_distr),len(expected_distr))

                # clean distributions of zeros (including a check)
                obs_distr = []
                exp_distr = []
                for o, e in zip(observed_distr, expected_distr):
                    if e == 0:
                        self.assertEqual(o,0)
                    else:
                        obs_distr.append(o)
                        exp_distr.append(e)

                observed_distr = np.array(obs_distr)
                expected_distr = np.array(exp_distr)

                # Chi-Square-Test
                chi_s, p_val = chisquare(observed_distr, f_exp=expected_distr)
                # print("chi_s = {}, p_val = {}".format(chi_s, p_val))

                if p_val < self.significance_level:
                    rejections += 1

            # go to another assignment
            for flip in random.sample(range(1,n),self.jump_range):
                ctx.update(flip)

            print("rejections = {}".format(rejections))
            self.assertTrue(rejections <= self.max_failure)


class TestSolver(unittest.TestCase):
    def setUp(self):
        random.seed()

        cases = 1 if __debug__ else 100

        n = 128 
        r = 4.2

        formulae = [
            Formula.generate_satisfiable_formula(n,r)
            for _ in range(0,cases)
        ]

        self.solver_setup = dict(
            max_flips     = n*5,
            max_tries     = 100,
            formulae      = formulae,
            max_run_time  = 20,
            cases         = cases,
            min_successes = cases // 100,
        )


    def generic_test_solver(self, solver):
        successes = 0
        run_time_exceeded = 0
        for formula in self.solver_setup['formulae']:
            assgn, measurement = solver(
                formula,
                TestMeasurement,
                self.solver_setup['max_tries'],
                self.solver_setup['max_flips'],
            )
            if assgn:
                self.assertTrue(measurement.flips > 0)
                self.assertTrue(formula.is_satisfied_by(assgn))
                successes += 1

            if measurement.get_run_time() >= self.solver_setup['max_run_time']:
                run_time_exceeded += 1

        print("{} successes".format(successes), end=' ')
        self.assertTrue(successes >= self.solver_setup['min_successes'])

        #self.assertTrue(
        #    run_time_exceeded < self.solver_setup['cases'] - self.solver_setup['min_successes']
        #)


    def test_solver(self):
        pass
