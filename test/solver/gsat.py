from functools import partial

from test.solver.generic_solver import TestSolver, TestDistribution

from src.solver.generic_solver import Context
from src.solver.gsat import gsat, gsat_heuristic, gsat_distribution
from src.solver.utils import DiffScores

class TestGSATDistr(TestDistribution):
    def test_distr(self):
        self.generic_test_distribution_against_heuristic(
            partial(Context, DiffScores),
            gsat_heuristic(),
            gsat_distribution(),
        )

class TestGSAT(TestSolver):
    def test_solver(self):
        self.generic_test_solver(gsat)
