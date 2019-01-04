from functools import partial

from test.solver.generic_solver import TestSolver, TestDistribution

from src.solver.generic_solver import Context
from src.solver.walksat import walksat, walksat_heuristic, walksat_distribution
from src.solver.utils import Scores

class TestWalkSATDistr(TestDistribution):
    def test_distr(self):
        self.generic_test_distribution_against_heuristic(
            partial(Context, Scores),
            walksat_heuristic(noise_param=0.57),
            walksat_distribution(noise_param=0.57)
        )


class TestWalkSAT(TestSolver):
    def test_solver(self):
        self.generic_test_solver(partial(walksat,noise_param=0.57))
