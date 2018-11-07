from test.solver.generic_solver import TestSolver
from src.solver.probsat import probsat
from functools import partial

class TestProbSAT(TestSolver):
    def test_solver(self):
        self.generic_test_solver(
            partial(
                probsat,
                c_break = 2.3,
                phi = 'poly',
            )
        )
