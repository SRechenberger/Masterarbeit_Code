import unittest
import random
import os

from functools import partial

from src.formula import Formula
from src.experiment.measurement import EntropyMeasurement
from src.experiment.utils import FormulaSupply



class TestEntropyMeasurement(unittest.TestCase):
    def setUp(self):
        random.seed()
        self.sample_size = 3
        self.pool_dir = 'test_files'
        number_formulae = 10
        Formula.generate_formula_pool(
            'test_files',
            number_formulae,
            10,
            4.2,
            poolsize = 3
        )
        self.dirs = random.sample(
            list(
                map(
                    partial(os.path.join, self.pool_dir),
                    os.listdir(self.pool_dir)
                )
            ),
            10
        )


    def test_measure_tms_count(self):
        for _,f in FormulaSupply(self.dirs):
            m = EntropyMeasurement(f,f.num_vars)
            m.init_run(f.satisfying_assignment)
            d = m.tms_steps
            for i in range(1,f.num_vars+1):
                m.count(i)

            self.assertEqual(len(d),f.num_vars)
            for (s1,s2),v in d.items():
                    self.assertEqual(v,1)
                    self.assertTrue(s1 == s2-1)

            for i in range(f.num_vars,0,-1):
                m.count(i)

            self.assertFalse((0,0) in d)
            self.assertFalse((f.num_vars,f.num_vars) in d)

            self.assertEqual(len(d),2*f.num_vars)

            for (s1,s2),v in d.items():
                    self.assertEqual(v,1)
                    self.assertTrue(s1 == s2-1 or s1 == s2+1)
