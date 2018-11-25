from test.solver.generic_solver import TestSolver, TestDistribution
from src.solver.probsat import probsat, probsat_heuristic, probsat_distribution
from src.solver.walksat import DefensiveContext
from functools import partial

class TestWalkSATDistr(TestDistribution):
    def test_distr(self):
        self.generic_test_distribution_against_heuristic(
            DefensiveContext,
            probsat_heuristic(int(self.n * self.r), 2.3),
            probsat_distribution(int(self.n * self.r), 2.3),
        )

class TestProbSAT(TestSolver):
    def test_solver(self):
        self.generic_test_solver(
            partial(
                probsat,
                c_break = 2.3,
                phi = 'poly',
            )
        )
