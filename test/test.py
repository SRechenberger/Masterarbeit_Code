import unittest
import random
import os
from src.solver.utils import Assignment, Falselist, Formula, Scores
from src.experiment.utils import DummyMeasurement, FormulaSupply
from src.solver.gsat import gsat
from src.solver.walksat import walksat
from src.solver.probsat import probsat

if __debug__:
    print("DEBUG")



class TestSolvers(unittest.TestCase):
    def setUp(self):
        random.seed()

        self.n = 128
        self.r = 4.0

        self.setup = dict(
            gsat    = dict(max_flips = int(self.n / 3), max_tries = 5*6),
            walksat = dict(max_flips = self.n * 3, max_tries = 5),
            probsat = dict(max_flips = self.n * 3, max_tries = 5)
        )
        dirname = 'test/testfiles'
        self.paths = random.sample(
            list(map(
                lambda fname: os.path.join(dirname, fname),
                filter(
                    lambda fname: fname.endswith('.cnf'),
                    os.listdir(dirname)
                )
            )),
            2
        )
        self.buffsize = 5
        self.cases = len(self.paths)


    def test_gsat(self):
        successes = 0
        for formula in FormulaSupply(self.paths, self.buffsize):
            measurement = DummyMeasurement()
            assgn = gsat(
                formula,
                self.setup['gsat']['max_tries'],
                self.setup['gsat']['max_flips'],
                measurement
            )
            if assgn:
                self.assertTrue(
                    measurement.flips % self.setup['gsat']['max_flips'] > 0
                )
                self.assertTrue(formula.is_satisfied_by(assgn))
                successes += 1

        self.assertTrue(successes > 0)
        print('GSAT successes: {}/{}'.format(successes,self.cases))


    def test_walksat(self):
        successes = 0
        rho = 0.57
        for formula in FormulaSupply(self.paths, self.buffsize):
            measurement = DummyMeasurement()
            assgn = walksat(
                rho,
                formula,
                self.setup['walksat']['max_tries'],
                self.setup['walksat']['max_flips'],
                measurement
            )
            if assgn:
                self.assertTrue(
                    measurement.flips % self.setup['walksat']['max_flips'] > 0
                )
                self.assertTrue(formula.is_satisfied_by(assgn))
                successes += 1

        self.assertTrue(successes > 0)
        print('WalkSAT successes: {}/{}'.format(successes,self.cases))


    def test_probsat(self):
        successes = 0
        c_make, c_break = 0.0,2.3
        for formula in FormulaSupply(self.paths, self.buffsize):
            measurement = DummyMeasurement()
            assgn = probsat(
                c_make,
                c_break,
                'poly',
                formula,
                self.setup['probsat']['max_tries'],
                self.setup['probsat']['max_flips'],
                measurement
            )
            if assgn:
                self.assertTrue(
                    measurement.flips % self.setup['probsat']['max_flips'] > 0
                )
                self.assertTrue(formula.is_satisfied_by(assgn))
                successes += 1

        self.assertTrue(successes > 0)
        print('ProbSAT successes: {}/{}'.format(successes,self.cases))


class TestFormula(unittest.TestCase):
    def setUp(self):
        random.seed()
        self.cases = 10 if __debug__ else 500

    def test_random_creation_and_reading(self):
        for i in range(0,self.cases):
            f = Formula.generate_satisfiable_formula(500, 4.2)
            self.assertEqual(f, Formula(dimacs = str(f)))

    def test_random_creation(self):
        for i in range(0,self.cases):
            n = random.randrange(10,1001)
            r = random.randrange(20,42)/10
            f = Formula.generate_satisfiable_formula(n, r)
            self.assertTrue(abs(f.num_clauses - n * r) < 2)

    def test_satisfiable_assignment(self):
        """This test really should not fail """
        for i in range(0,self.cases):
            n = random.randrange(10,1001)
            r = random.randrange(20,42)/10
            f = Formula.generate_satisfiable_formula(n,r)
            self.assertTrue(f.is_satisfied_by(f.satisfying_assignment))

    def test_hardness(self):
        n = 500
        for i in range(0,self.cases):
            f = Formula.generate_satisfiable_formula(n, 4.2)
            atoms = 0
            for var in range(1,n+1):
                if len(f.get_occurrences(var)) > len(f.get_occurrences(-var)):
                    atoms += 1
                atoms *= 2
            a = Assignment(atoms, n)
            self.assertFalse(f.is_satisfied_by(a))



if __name__ == '__main__':
    unittest.main()
