from test.solver.generic_solver import TestSolver, TestDistribution
from src.solver.walksat import walksat, walksat_heuristic, walksat_distribution, DefensiveContext
from functools import partial

class TestWalkSATDistr(TestDistribution):
    def test_distr(self):
        self.generic_test_distribution_against_heuristic(
            DefensiveContext,
            walksat_heuristic(noise_param=0.57),
            walksat_distribution(noise_param=0.57)
        )


class TestWalkSAT(TestSolver):
    def test_solver(self):
        self.generic_test_solver(partial(walksat,noise_param=0.57))
