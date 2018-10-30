import unittest
import random

from src.experiment.experiment import Experiment
from src.experiment.utils import Measurement
from src.solver.generic_solver import Context
from src.solver.gsat import gsat
from src.solver.walksat import walksat
from src.solver.probsat import probsat
from src.solver.utils import Formula
from src.utils import *

class TestExperiment(unittest.TestCase):

    def setUp(self):
        random.seed()
        self.sample_size = 3
        self.pool_dir = 'test_files'
        number_formulae = 10
        Formula.generate_formula_pool(
            'test_files',
            number_formulae,
            256,
            4.2,
            poolsize = 3
        )


    def test_experiment_with_gsat(self):
        experiment = Experiment(
            self.pool_dir,
            self.sample_size,
            'gsat',
            10,500,Measurement,
            poolsize = 3
        )
        results = experiment.run_experiment()
        self.assertTrue(len(results),self.sample_size)

    def test_experiment_with_walksat(self):
        experiment = Experiment(
            self.pool_dir,
            self.sample_size,
            'walksat',
            10,500,Measurement,
            0.57,
            poolsize = 3
        )
        results = experiment.run_experiment()
        self.assertTrue(len(results),self.sample_size)

    def test_experiment_with_probsat(self):
        experiment = Experiment(
            self.pool_dir,
            self.sample_size,
            'probsat',
            10,500,Measurement,
            0.0,2.3,'poly',
            poolsize = 3
        )
        results = experiment.run_experiment()
        self.assertTrue(len(results),self.sample_size)

