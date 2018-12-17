import unittest
import random
import os

from functools import partial

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
        self.sample_size = 10
        self.test_num = random.randrange(0,2**6)
        self.pool_dir = f'TEST_EXPERIMENT_{self.test_num:04X}'
        self.n = 64
        self.db = f'db_{self.test_num:04X}.db'
        Formula.generate_formula_pool(
            self.pool_dir,
            self.sample_size,
            self.n,
            4.2,
            poolsize=3
        )
        self.pool = list(map(partial(os.path.join, self.pool_dir), os.listdir(self.pool_dir)))

    def doCleanups(self):
        try:
            for file in self.pool:
                os.remove(file)
            os.remove(self.db)
            os.rmdir(self.pool_dir)
        except:
            pass

    def test_experiment_with_gsat(self):
        experiment = DynamicExperiment(
            self.pool,
            'gsat',
            dict(
                max_tries=10,
                max_flips=self.n*5,
                noise_param=0
            ),
            EntropyMeasurement,
            poolsize = 3,
            database=self.db,
        )
        results = experiment()
        self.assertEqual(len(results),self.sample_size)
        experiment.save_results()


    def test_experiment_with_walksat(self):
        experiment = DynamicExperiment(
            self.pool,
            'walksat',
            dict(
                max_tries=10,
                max_flips=self.n*5,
                noise_param=0.57
            ),
            EntropyMeasurement,
            poolsize = 3,
            database=self.db,
        )
        results = experiment()
        self.assertEqual(len(results),self.sample_size)
        experiment.save_results()


    def test_experiment_with_probsat(self):
        experiment = DynamicExperiment(
            self.pool,
            'probsat',
            dict(
                max_tries=10,
                max_flips=self.n*5,
                noise_param=2.3
            ),
            EntropyMeasurement,
            poolsize = 3,
            database=self.db,
        )
        results = experiment()
        self.assertEqual(len(results),self.sample_size)
        experiment.save_results()

