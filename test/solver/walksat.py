from test.solver.generic_solver import TestSolver
from src.solver.walksat import walksat
from functools import partial

class TestWalkSAT(TestSolver):
    def test_solver(self):
        rho = 0.57
        self.generic_test_solver(partial(walksat,rho))
