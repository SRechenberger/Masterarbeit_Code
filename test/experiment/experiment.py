import unittest
import random

from src.experiment.experiment import DynamicExperiment
from src.experiment.measurement import EntropyMeasurement
from src.solver.generic_solver import Context
from src.solver.gsat import gsat
from src.solver.walksat import walksat
from src.solver.probsat import probsat
from src.formula import Formula

class TestExperiment(unittest.TestCase):

    def setUp(self):
        random.seed()
        self.sample_size = 3
        self.pool_dir = 'test_files'
        number_formulae = 10
        self.n = 256
        Formula.generate_formula_pool(
            'test_files',
            number_formulae,
            self.n,
            4.2,
            poolsize = 3
        )


    def test_experiment_with_gsat(self):
        experiment = DynamicExperiment(
            self.pool_dir,
            self.sample_size,
            'gsat',
            dict(),
            10,self.n*3,
            EntropyMeasurement,
            poolsize = 3
        )
        results = experiment()
        self.assertEqual(len(results),self.sample_size)
        experiment.save_results()


    def test_experiment_with_walksat(self):
        experiment = DynamicExperiment(
            self.pool_dir,
            self.sample_size,
            'walksat',
            dict(rho=0.57),
            10,self.n*3,
            EntropyMeasurement,
            poolsize = 3,
        )
        results = experiment()
        self.assertEqual(len(results),self.sample_size)
        experiment.save_results()


    def test_experiment_with_probsat(self):
        experiment = DynamicExperiment(
            self.pool_dir,
            self.sample_size,
            'probsat',
            dict(c_break=2.3,phi='poly'),
            10,self.n*3,
            EntropyMeasurement,
            poolsize = 3,
        )
        results = experiment()
        self.assertEqual(len(results),self.sample_size)
        experiment.save_results()

