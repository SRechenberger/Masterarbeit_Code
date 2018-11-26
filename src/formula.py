"""
# Module src.formula

## Contents
    - class Formula
    - class Assignment

## Side Effects
    - if python version < 3.6, a simple version of random.choices
      is added to module random
"""


import random
import platform
import os
import re
import multiprocessing as mp

from collections.abc import Sequence


if platform.sys.version_info.major < 3:
    raise Exception("Must be Python 3")


if platform.sys.version_info.minor < 6:

    def choices(seq, weights=None):
        """ simplified version of random.choices included in python 3.6 """
        if not weights:
            weights = [1/len(seq) for _ in range(0, len(seq))]

        acc = 0
        dice = random.random()
        for prob, val in zip(weights, seq):
            acc += prob
            if acc > dice:
                return [val]

        return []

    random.choices = choices


class Formula:
    """ CNF formulae in DIMACS format """

    def __init__(self, dimacs=None, clauses=None, num_vars=None, sat_assignment=None):
        """ Load a formula from a .cnf (DIMACS) file """
        # check for argument validity
        assert not dimacs or isinstance(dimacs, str),\
            "dimacs = {} :: {} is no str".format(dimacs, type(dimacs))
        assert not clauses or isinstance(clauses, Sequence),\
            "clauses = {} :: {} is no Sequence".format(clauses, type(clauses))
        assert not num_vars or isinstance(num_vars, int),\
            "num_vars = {} :: {} is no int".format(num_vars, type(num_vars))
        assert not num_vars or num_vars > 0,\
            "num_vars = {} <= 0".format(num_vars)
        assert not sat_assignment or isinstance(sat_assignment, Assignment),\
            "sat_assignment = {} :: {} is no Assignment".format(
                sat_assignment,
                type(sat_assignment)
            )


        # init variables
        self.clauses = []
        self.num_clauses = 0
        self.num_vars = 0
        self.comments = []
        self.occurrences = []
        self.max_clause_length = 0
        self.satisfying_assignment = None

        # parse the file.
        if dimacs:
            numbers = re.compile(r'-?\d+')           # find numbers
            hex_numbers = re.compile(r'-?0x[0-9a-fA-F]+') # find hex numbers

            for line in dimacs.splitlines():
                if line[0] == 'c':
                    if line.startswith('c assgn'):
                        hex_val, = hex_numbers.findall(line)
                    else:
                        self.comments.append(line)
                elif line[0] == 'p':
                    num_vars, num_clauses = numbers.findall(line)
                    self.num_vars = int(num_vars)
                    self.num_clauses = int(num_clauses)
                    self.satisfying_assignment = Assignment(int(hex_val, 16), int(num_vars))
                else:
                    self.clauses.append(list(map(int, numbers.findall(line)))[:-1])
                    if len(self.clauses[-1]) > self.max_clause_length:
                        self.max_clause_length = len(self.clauses[-1])

        # or use the given stuff
        elif not dimacs and clauses and num_vars and sat_assignment:
            self.satisfying_assignment = sat_assignment
            self.clauses = clauses
            self.num_clauses = len(clauses)
            self.num_vars = num_vars
            self.max_clause_length = max(map(len, clauses))

        else:
            raise ValueError(
                "Either 'dimacs' or 'clauses', 'num_vars' and 'sat_assignment' must be provided"
            )

        self.occurrences = [[] for _ in range(0, self.num_vars*2+1)]

        for clause_idx, clause in enumerate(self.clauses):
            for lit in clause:
                self.occurrences[self.num_vars + lit].append(clause_idx)

        self.max_occs = 0
        for occ in self.occurrences:
            if len(occ) > self.max_occs:
                self.max_occs = len(occ)

        self.ratio = self.num_clauses / self.num_vars


    def __eq__(self, formula):
        if not formula:
            return False

        return all([
            self.num_vars == formula.num_vars,
            self.clauses == formula.clauses,
            str(self.satisfying_assignment) == str(formula.satisfying_assignment)
        ])


    def __str__(self):
        """ Represent formula in DIMACS format """

        to_return = "\n".join(self.comments)

        #for comment in self.comments:
        #    to_return += comment
        to_return += 'c assgn {}\n'.format(str(self.satisfying_assignment))
        to_return += 'p cnf {} {}\n'.format(self.num_vars, self.num_clauses)
        for clause in self.clauses:
            for literal in clause:
                to_return += '{} '.format(literal)
            to_return += '0\n'

        return to_return


    def is_satisfied_by(self, assignment):
        """ Checks, whether self is satisfied by the given assignment """
        assert isinstance(assignment, Assignment),\
            "assignment is no Assignment"

        for clause in self.clauses:
            true_clause = False
            for literal in clause:
                if assignment.is_true(literal):
                    true_clause = True
                    break
            if not true_clause:
                return False

        return True


    def get_occurrences(self, literal):
        """ Returns the list of occurrences of literal """
        assert isinstance(literal, int),\
            "literal = {} :: {} is no int".format(literal, type(literal))
        assert literal != 0,\
            "literal = {} == 0".format(literal)

        return self.occurrences[self.num_vars + literal]


    @staticmethod
    def generate_satisfiable_formula(num_vars, ratio, clause_length=3, rand_gen=random):
        """ Randomly generates a satisfying formula """
        assert isinstance(clause_length, int),\
            "clause_length = {} :: {} is no int".format(clause_length, type(clause_length))
        assert clause_length > 0,\
            "clause_length = {} <= 0".format(clause_length)
        assert clause_length == 3,\
            'Method \'generate_satisfiable_formula\' only implemented for 3CNF yet.'
        assert isinstance(num_vars, int),\
            "num_vars = {} :: {} is no int".format(num_vars, type(num_vars))
        assert num_vars > 0,\
            "num_vars = {} <= 0".format(num_vars)
        assert isinstance(ratio, float),\
            "ratio = {} :: {} is no float".format(ratio, type(ratio))
        assert ratio > 0,\
            "ratio = {} <= 0".format(ratio)

        # optional arguments
        satisfying_assignment = Assignment.generate_random_assignment(
            num_vars,
            rand_gen=rand_gen,
        )

        num_clauses = int(ratio * num_vars)
        clauses = []
        probs = {1: 0.191, 2: 0.118, 3: 0.073}
        for _ in range(0, num_clauses + 1):
            variables = rand_gen.sample(range(1, num_vars+1), clause_length)

            all_clauses = [[]]
            for var in variables:
                all_clauses = list(map(lambda clause: [var] + clause, all_clauses)) \
                            + list(map(lambda clause: [-var] + clause, all_clauses))

            sat = lambda lit: 1 if satisfying_assignment.is_true(lit) else 0
            possible_clauses, weights = [], []
            for clause in all_clauses:
                sat_vars = sum(map(sat, clause))
                if sat_vars > 0:
                    possible_clauses.append(clause)
                    weights.append(probs[sat_vars])

            clause, = rand_gen.choices(possible_clauses, weights=weights)
            clauses.append(clause)

        formula = Formula(
            clauses=clauses,
            num_vars=num_vars,
            sat_assignment=satisfying_assignment
        )

        assert formula.is_satisfied_by(satisfying_assignment),\
            "satisfying_assignment = {} does not satisfy formula".format(satisfying_assignment)

        return formula


    @staticmethod
    def generate_formula_pool(
            directory,
            number,
            num_vars,
            ratio,
            clause_length=3,
            poolsize=1,
            verbose=False):
        """ Generates a set of random formulae and writes them into the given directory """
        assert isinstance(directory, str),\
            "directory = {} :: {} is no str".format(directory, type(directory))
        assert isinstance(number, int),\
            "number = {} :: {} is no int".format(number, type(number))
        assert number > 0,\
            "number = {} <= 0".format(number)
        assert isinstance(num_vars, int),\
            "num_vars = {} :: {} is no int".format(num_vars, type(num_vars))
        assert num_vars > 0,\
            "num_vars = {} <= 0".format(num_vars)
        assert isinstance(ratio, float),\
            "ratio = {} :: {} is no float".format(ratio, type(ratio))
        assert ratio > 0,\
            "ratio = {} <= 0".format(ratio)
        assert isinstance(clause_length, int),\
            "clause_length = {} :: {} is no int".format(clause_length, type(clause_length))
        assert clause_length > 0,\
            "clause_length = {} <= 0".format(clause_length)

        try:
            os.mkdir(directory)
        except FileExistsError:
            pass

        with mp.Pool(processes=poolsize) as pool:
            future_formulae = []
            for _ in range(0, number):
                future_formula = pool.apply_async(
                    Formula.generate_satisfiable_formula,
                    (
                        num_vars,
                        ratio,
                        clause_length
                    )
                )
                future_formulae.append(future_formula)

            idx = 0
            for future_formula in future_formulae:
                formula = future_formula.get()
                filename = 'n{}-r{:.2f}-k{}-{:016X}.cnf'.format(
                    num_vars,
                    ratio,
                    clause_length,
                    hash(formula),
                )
                with open(os.path.join(directory, filename), 'w') as target:
                    target.write(str(formula))

                del future_formulae[idx]
                idx += 1

                if verbose:
                    print(
                        'File {} written.'.format(
                            os.path.join(directory, filename)
                        )
                    )



    def __hash__(self):
        return abs(
            hash(
                '{}{}{}{}{}'.format(
                    self.num_vars,
                    self.max_clause_length,
                    self.ratio,
                    str(self.satisfying_assignment),
                    id(self)
                )
            )
        )


class Assignment:
    """ Assignment modelled as an array of bits """

    @staticmethod
    def generate_random_assignment(num_vars, rand_gen=random):
        """ Randomly generating a number between
        0 and 2^num_vars, converting it into an assignment,
        and returning it
        """
        assert isinstance(num_vars, int),\
            "num_vars = {} :: {} is no int".format(num_vars, type(num_vars))
        assert num_vars > 0,\
            "num_vars = {} <= 0".format(num_vars)

        return Assignment(
            rand_gen.randrange(0, pow(2, num_vars)),
            num_vars,
        )


    @staticmethod
    def atoms_from_integer(number):
        """ Takes a number and converts it into a list of booleans """
        atoms = []
        num = number
        while num > 0:
            atoms.append(num % 2 == 1)
            num //= 2

        return atoms


    @staticmethod
    def integer_from_atoms(atoms):
        """ Takes a list of booleans and converts it into a number """
        num = 0
        tmp = atoms.copy()
        while tmp:
            num *= 2
            num += 1 if tmp.pop() else 0

        return num


    def flip(self, var_index):
        """ Flips the variable with the index given """
        assert isinstance(var_index, int),\
            "var_index = {} :: {} is no int".format(var_index, type(var_index))
        assert var_index > 0,\
            "var_index = {} <= 0".format(var_index)

        self.atoms[var_index-1] = not self.atoms[var_index-1]


    def get_value(self, var_index):
        """ Returns the assignment to the variable with the index given """
        assert isinstance(var_index, int),\
            "var_index = {} :: {} is no int".format(var_index, type(var_index))
        assert var_index > 0,\
            "var_index = {} <= 0".format(var_index)

        return self.atoms[var_index-1]


    def __getitem__(self, var_index):
        return self.get_value(var_index)

    def __setitem__(self, var_index, value):
        self.atoms[var_index] = True if value else False

    def __delitem__(self, var_index):
        pass


    def is_true(self, literal):
        """ Checks, whether the given literal is true or false under self """
        assert isinstance(literal, int),\
            "literal = {} :: {} is no int".format(literal, type(literal))
        assert literal != 0,\
            "literal = {} == 0".format(literal)

        val = self.get_value(abs(literal))
        return val if literal > 0 else not val


    def __init__(self, atoms, num_vars):
        """ Generate an assignment from an integer or a list of booleans """
        assert isinstance(atoms, (int, list)),\
            "atoms = {} :: {} is neither int nor list".format(atoms, type(atoms))
        assert not isinstance(atoms, list) or len(atoms) == num_vars,\
            "len(atoms) = {} != {} = num_vars".format(len(atoms), num_vars)

        if isinstance(atoms, list):
            self.atoms = atoms

        else:
            self.atoms = Assignment.atoms_from_integer(atoms)
            self.atoms += [False]*(num_vars-len(self.atoms))

        self.num_vars = num_vars


    def __iter__(self):
        return iter(self.atoms)


    def __str__(self):
        """ Converts the assignment to a hex literal with 0x prefix """
        return hex(Assignment.integer_from_atoms(self.atoms))


    def hamming_dist(self, assgn):
        """ Calculates the hamming distance between self and assgn """
        assert isinstance(assgn, Assignment),\
            "assgn = {} :: {} is no Assignment".format(assgn, type(assgn))
        assert assgn.num_vars == self.num_vars,\
            "assgn.num_vars = {} != {} = self.num_vars".format(
                assgn.num_vars,
                self.num_vars
            )

        dist = 0
        for i in range(1, self.num_vars+1):
            dist += 1 if self[i] != assgn[i] else 0

        return dist

    def hamming_sets(self, assgn):
        """ Calculate the set of variables, in which both assignments differ or are equal """
        assert isinstance(assgn, Assignment),\
            "assgn = {} :: {} is no Assignment".format(assgn, type(assgn))
        assert self.num_vars == assgn.num_vars,\
            "self.num_vars = {} != {} = assgn.num_vars".format(self.num_vars, assgn.num_vars)

        different = []
        same = []

        for i, a_i, b_i in zip(range(1, self.num_vars+1), iter(self), iter(assgn)):
            if a_i == b_i:
                same.append(i)

            else:
                different.append(i)

        return different, same


    def negation(self):
        """ Returns the bitwise negation of the assignment """

        atoms = self.atoms.copy()
        for i in enumerate(atoms):
            atoms[i] = not atoms[i]

        return Assignment(
            atoms,
            self.num_vars,
        )


    def copy(self):
        """ Copies the assignment """
        # TODO isn't there a built in protocol?
        return type(self)(self.atoms.copy(), self.num_vars)
