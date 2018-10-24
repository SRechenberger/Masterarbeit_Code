import unittest
import random
import os

from test.solver.generic_solver import TestSolver
from src.solver.gsat import gsat

class TestGSAT(TestSolver):
    def test_solver(self):
        self.generic_test_solver(gsat)
