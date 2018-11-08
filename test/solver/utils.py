import unittest
import random
import os

from src.solver.utils import Assignment, Falselist, Formula, Scores
from src.experiment.utils import FormulaSupply

class TestAssignment(unittest.TestCase):
    def setUp(self):
        random.seed()
        self.maxDiff = None

    def test_creation(self):
        for i in range(1,1000):
            num_vars = random.randrange(1,i+1)
            assgn1 = Assignment.generate_random_assignment(num_vars)
            assgn2 = Assignment(int(str(assgn1),16),num_vars)
            self.assertEqual(str(assgn1),str(assgn2))

    def test_flip(self):
        for i in range(1,1000):
            num_vars = random.randrange(1,i+1)
            number   = random.randrange(0,pow(2,num_vars))
            assgn    = Assignment(number, num_vars)
            self.assertEqual(hex(number), str(assgn))
            to_flip  = random.randrange(1,num_vars+1)
            assgn.flip(to_flip)
            number ^= 1 << (to_flip-1)
            self.assertEqual(hex(number), str(assgn))

    def test_index(self):
        for i in range(1,1000):
            num_vars = random.randrange(1,i+1)
            assgn    = Assignment.generate_random_assignment(num_vars)
            to_flip  = random.randrange(1,num_vars+1)
            old      = assgn[to_flip]
            assgn.flip(to_flip)
            self.assertNotEqual(old, assgn[to_flip])


class TestFalselist(unittest.TestCase):
    def setUp(self):
        random.seed()
        self.maxDiff = None

    def test_add(self):
        l = Falselist()
        t = set()
        xs = list(range(1,1000))
        random.shuffle(xs)
        for x in xs:
            l.add(x)
            t.add(x)
            self.assertEqual(set(l.lst),t)

    def test_remove(self):
        l = Falselist()
        xs = list(range(1,1000))
        random.shuffle(xs)
        for x in xs:
            l.add(x)
        for x in random.sample(xs, 100):
            l.remove(x)
        for k,v in l.mapping.items():
            self.assertEqual(k, l.lst[v])


class TestScores(unittest.TestCase):
    def setUp(self):
        random.seed()
        dirname = 'test_files'
        Formula.generate_formula_pool(
            dirname,
            10,
            256,
            4.2,
            poolsize=3
        )
        self.paths = list(map(
            lambda fname: os.path.join(dirname, fname),
            filter(
                lambda fname: fname.endswith('.cnf'),
                os.listdir(dirname)
            )
        ))
        self.buffsize = 5


    def test_creation_and_flip(self):
        def check_consistency(score, formula, falselist, assgn, samplesize):
            # all clauses in the false list should be unsat
            for cl_idx in falselist:
                for lit in formula.clauses[cl_idx]:
                    self.assertFalse(assgn.is_true(lit))

            for x in random.sample(range(1,formula.num_vars+1), samplesize):
                mk = 0
                for cl_idx in falselist:
                    if x in map(abs, formula.clauses[cl_idx]):
                        mk += 1
                self.assertEqual(mk, score.get_make_score(x))

                br = 0
                for clause in formula.clauses:
                    if x in map(abs,clause):
                        critical = 0
                        for lit in clause:
                            if assgn.is_true(lit) and critical > 0:
                                critical = 0
                                break
                            elif assgn.is_true(lit):
                                critical = abs(lit)
                        if x == critical:
                            br += 1
                self.assertEqual(br, score.get_break_score(x))
                self.assertEqual(
                    mk-br,
                    score.bucket_mapping[x]
                )
                self.assertTrue(abs(score.get_score_of_var(x)) <= formula.max_occs)


        for _, formula in FormulaSupply(self.paths, self.buffsize):
            n = formula.num_vars
            falselist = Falselist()
            assgn = formula.satisfying_assignment
            # may crash
            scores = Scores(formula, assgn, falselist)

            check_consistency(scores, formula, falselist, assgn, formula.num_vars // 2)

            # draw 100 times a sample of size n/2 from n variables for multiple flips of one variable
            to_flips = [i for _ in range(0,100) for i in random.sample(range(1,n+1),formula.num_vars // 2)]
            for to_flip in to_flips:
                scores.flip(to_flip, formula, assgn, falselist)

            check_consistency(scores, formula, falselist, assgn, formula.num_vars // 2)


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
