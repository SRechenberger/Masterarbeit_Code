from functools import partial

from test.solver.generic_solver import TestSolver, TestDistribution

from src.solver.generic_solver import Context
from src.solver.probsat import probsat, probsat_heuristic, probsat_distribution
from src.solver.utils import Scores

class TestProbSATDistr(TestDistribution):
    def test_distr(self):
        self.generic_test_distribution_against_heuristic(
            partial(Context, Scores),
            probsat_heuristic(noise_param=2.3),
            probsat_distribution(noise_param=2.3),
        )

class TestProbSAT(TestSolver):
    def test_solver(self):
        self.generic_test_solver(
            partial(
                probsat,
                noise_param=2.3,
            )
        )
