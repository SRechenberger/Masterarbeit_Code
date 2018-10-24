from test.solver.generic_solver import TestSolver
from src.solver.probsat import probsat
from functools import partial

class TestProbSAT(TestSolver):
    def test_solver(self):
        c_make, c_break, func = 0.0, 2.3, 'poly'
        self.generic_test_solver(partial(probsat,c_make,c_break,func))
