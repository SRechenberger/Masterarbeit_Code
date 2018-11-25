import unittest
import random
import os
import re

from src.formula import Formula, Assignment

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

    def test_hamming_sets(self):
        for i in range(1,1000):
            n = 500
            assgn = Assignment.generate_random_assignment(n)
            assgn_2 = assgn.copy()
            sample_size = random.randrange(1,n+1)
            sample = set(random.sample(range(1,n+1), sample_size))
            for flip in sample:
                assgn_2.flip(flip)
            different, same = assgn.hamming_sets(assgn_2)
            self.assertEqual(sample, set(different))
            self.assertEqual(set(range(1,n+1)) - set(different), set(same))


class TestFormula(unittest.TestCase):
    def setUp(self):
        random.seed()
        self.cases = 10 if __debug__ else 500


    def test_random_creation_and_reading(self):
        for i in range(0,self.cases):
            f = Formula.generate_satisfiable_formula(500, 4.2)
            self.assertEqual(f, Formula(dimacs = str(f)))


    def test_occurrence_counting(self):
        for i in range(0,self.cases):
            f = Formula.generate_satisfiable_formula(500, 4.2)
            occ_count = {}
            for clause in f.clauses:
                for lit in clause:
                    if lit in occ_count:
                        occ_count[lit] += 1
                    else:
                        occ_count[lit] = 1

            for k,v in occ_count.items():
                self.assertEqual(
                    len(f.get_occurrences(k)),
                    v
                )
                self.assertLessEqual(v, f.max_occs)

    def test_occurrences(self):
        for i in range(0,self.cases):
            f = Formula.generate_satisfiable_formula(500,4.2)
            for i in range(1,501):
                pos_occs = f.get_occurrences(i)
                neg_occs = f.get_occurrences(-i)

                # validate positive occurrences
                for clause_idx in pos_occs:
                    self.assertTrue(i in f.clauses[clause_idx])

                # validate negative occurrences
                for clause_idx in neg_occs:
                    self.assertTrue(-i in f.clauses[clause_idx])


    def test_random_creation(self):
        for i in range(0,self.cases):
            n = random.randrange(10,1001)
            r = random.randrange(20,42)/10
            f = Formula.generate_satisfiable_formula(n, r)
            self.assertLess(f.num_clauses - n * r, 2)


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
