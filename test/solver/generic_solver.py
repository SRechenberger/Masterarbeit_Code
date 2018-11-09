import unittest
import random
import time

from src.formula import Formula
from src.experiment.utils import Measurement


class TestMeasurement(Measurement):
    def __init__(self, formula):
        self.flips = 0
        self.begin_time = time.time()

    def count(self, flipped_var):
        self.flips += 1

    def get_run_time(self):
        return time.time() - self.begin_time


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
