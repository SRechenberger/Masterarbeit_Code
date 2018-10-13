import random
class Formula:
    """ CNF formulae in DIMACS format """

    def __init__(self, filepath):
        """ Load a formula from a .cnf (DIMACS) file """
        # check for argument validity
        if not type(filepath) == str:
            raise TypeError("Argument 'filepath' was no string.")

        if not filepath.endswith('.cnf'):
            raise ValueError(filepath + " is no .cnf file.")

        # init variables
        self.clauses = []
        self.num_clauses = 0
        self.num_vars = 0
        self.comments = []
        self.occurrences = []
        self.max_clause_length = 0

        # parse the file.
        with open(filepath) as f:
            r = re.compile(r'-?\d+')           # find numbers
            rh = re.compile(r'-?0x[0-9a-fA-F]+') # find hex numbers

            for line in f:
                if line[0] == 'c':
                    if line.startswith('c assgn'):
                        hex_val = rh.findall(line)
                        self.satisfing_assignment = Assignment(hex_val)
                    self.comments.append(line)
                elif line[0] == 'p':
                    n, m = r.findall(line)
                    self.num_vars = int(n)
                    self.num_clauses = int(m)
                else:
                    self.clauses.append(list(map(int, r.findall(line)))[:-1])
                    if len(self.clauses[-1]) > self.max_clause_length:
                        self.max_clause_length = len(self.clauses[-1])

        for i in range(0, self.numVars*2+1):
            self.occurrences.append([])

        for idx in range(0, self.num_clauses):
            for literal in self.clauses[idx]:
                self.occurrences[self.numVars + literal].append(idx)

        self.max_occs = 0
        for occ in self.occurrences:
            if len(occ) > self.max_occs:
                self.max_occs = len(occ)

        self.ratio = self.num_clauses / self.num_vars
        self.is_init = True


    def __str__(self):
        """ Represent formula in DIMACS format """

        self.checkInit()

        toReturn = ''

        for comment in self.comments:
            toReturn += comment
        toReturn += 'p cnf {} {}\n'.format(self.num_vars, self.num_clauses)
        for clause in self.clauses:
            for literal in clause:
                toReturn += '{} '.format(literal)
            toReturn += '0\n'

        return toReturn


    def is_satisfied_by(self, assignment):
        if not isinstance(assignment, Assignment):
            raise TypeError('The given argument is no assignment.')

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
        return self.occurrences[self.num_vars + literal]


    def generate_satisfiable_formula(clause_length, num_vars, ratio, seed=None):
        raise RuntimeError(
            'Method \'generate_satisfiable_formula\' not implemented yet.'
        )


class Falselist:
    """ Models a list with no need for order,
    for the list of unsatisfied clauses.
    """
    def __init__(self):
        self.lst = []
        self.mapping = {}


    def remove(self, idx):
        if not type(idx) == int:
            raise TypeError('Type of idx :: {} is not int'
                            .format(type(idx)))
        if idx < 0:
            raise IndexError('idx = {} is negative'
                             .format(idx))
        if idx >= len(self.lst):
            raise IndexError('idx = {} is greater or equal to len(lst) = {}'
                             .format(idx, len(self.lst)))

        tmp = self.lst[idx]
        if idx == len(self.lst)-1:
            self.lst.pop()
        else:
            self.lst[idx] = self.lst.pop()
            self.mapping[self.lst[idx]] = idx
        del self.mapping[tmp]


    def add(self, elem):
        self.lst.append(elem)
        self.mapping[elem] = len(self.lst)-1


    def __len__(self):
        return len(self.lst)



class Assignment:
    """ Assignment modelled as an array of bits """

    def generate_random_assignment(num_vars):
        """ Randomly generating a number between
        0 and 2^num_vars, converting it into an assignment,
        and returning it
        """
        if type(num_vars) is not int:
            raise TypeError('num_vars is not int')
        if num_vars <= 0:
            raise ValueError('num_vars must be positive ({})'.format(num_vars))

        return Assignment(
            random.randrange(0,pow(2,num_vars)),
            num_vars,
        )


    def atoms_from_integer(number):
        """ Takes a number and converts it into a list of booleans """
        atoms = []
        n = number
        while n > 0:
            atoms.append(n % 2 == 1)
            n //= 2
        return atoms


    def integer_from_atoms(atoms):
        """ Takes a list of booleans and converts it into a number """
        n = 0
        tmp = atoms.copy()
        while tmp:
            n *= 2
            n += 1 if tmp.pop() else 0

        return n


    def flip(self, var_index):
        """ Flips the variable with the index given """
        if type(var_index) is not int:
            raise TypeError('var_index is not int')
        if var_index <= 0 or self.num_vars < var_index:
            raise ValueError(
                '0 < var_index ({}) <= num_vars ({}) must hold'
                .format(var_index,self.num_vars)
            )

        self.atoms[var_index-1] = not self.atoms[var_index-1]


    def get_value(self, var_index):
        """ Returns the assignment to the variable with the index given """
        if type(var_index) is not int:
            raise TypeError('var is not int')
        if var_index <= 0 or self.num_vars < var_index:
            raise ValueError('0 < vars <= num_vars must hold')

        return self.atoms[var_index+1]


    def is_true(self, literal):
        if type(literal) is not int:
            raise TypeError('literal is not int')
        if literal == 0:
            raise ValueError('literal is equal to 0')

        t = self.get_value(abs(literal))
        return t if literal > 0 else not t


    def __init__(self, number, num_vars):
        """ Generate an assignment from an integer """
        if type(number) is not int:
            raise TypeError('number is not int')

        self.atoms = Assignment.atoms_from_integer(number)
        self.atoms += [False]*(num_vars-len(self.atoms))
        self.num_vars = num_vars


    def __str__(self):
        """ Converts the assignment to a hex literal with 0x prefix """
        return hex(Assignment.integer_from_atoms(self.atoms))



class Breakscore:
    def __init__(self, formula, assignment, falselist):
        if not isinstance(formula, Formula):
            raise TypeError("The given object formula={} is no cnf-formula."
                            .format(formula))
        if not isinstance(assignment, Assignment):
            raise TypeError("The given object assignment={} is no assignment."
                            .format(assignment))
        if not isinstance(falselist, Falselist):
            raise TypeError("The given object falselist={} is no assignment."
                            .format(falselist))


        self.crit_var = []
        self.num_true_lit = []
        self.breaks = {}

        # Begin at clause 0
        clause_idx = 0
        # for each clause of the formula
        for clause in formula.clauses:
            # init the criticial variable
            self.crit_var.append(None)
            # init the number of true literals for this clause
            self.num_true_lit.append(0)
            # a local variable to track the critical variable
            crit_var = 0
            # for each literal of the clause
            for lit in clause:
                # if the literal is satisfied
                if assignment.is_true(lit):
                    # it MAY BE the critical variable of the clause
                    crit_var = abs(lit)
                    # there is one more true literal
                    self.num_true_lit[-1] += 1

            # if after the traverse of the clause there is exactly one true
            # literal
            if self.num_true_lit[-1] == 1:
                # it is the critical literal
                self.crit_var[-1] = crit_var
                # thus it breaks the clause
                self.increment_break_score(crit_var)

            # if there is no true literal
            elif self.num_true_lit[-1] == 0:
                # add the clause to the list of false clauses
                falselist.add(clause_idx)

            # next clause
            clause_idx += 1


    def increment_break_score(self, variable):
        if not type(variable) == int:
            raise TypeError("variable={} is not of type int.".format(variable))

        if variable in self.breaks:
            self.breaks[variable] += 1
        else:
            self.breaks[variable] = 1


    def get_break_score(self, variable):
        if not type(variable) == int:
            raise TypeError("variable={} is not of type int.".format(variable))

        if variable in self.breaks:
            return self.breaks[variable]
        else:
            return 0


    def flip(self, variable, formula, assignment, falselist):
        if type(variable) != int:
            raise TypeError("variable={} is not of type int.".format(variable))
        if not isinstance(formula, CNF):
            raise TypeError("The given object formula={} is no cnf-formula."
                            .format(formula))
        if not isinstance(assignment, Assignment):
            raise TypeError("The given object assignment={} is no assignment."
                            .format(assignment))
        if not isinstance(falselist, Falselist):
            raise TypeError("The given object falselist={} is no assignment."
                            .format(falselist))

        # a[v] = -a[v]
        assignment.flip(variable)
        # satisfyingLiteral = a[v] ? v : -v
        satisfying_literal = variable if assignment.is_true(variable) else -variable
        # falsifyingLiteral = a[v] ? -v : v
        # isn't this just -satisfyingLiteral ?
        falsifying_literal = -variable if assignment.is_true(variable) else variable
        occs = formula.occurrences
        for clause_idx in formula.get_occurrences(satisfying_literal):
            if self.num_true_lit[clause_idx] == 0:
                falselist.remove(falselist.mapping[clause_idx])
                self.increment_break_score(variable)
                self.crit_var[clause_idx] = variable
            elif self.num_true_lit[clause_idx] == 1:
                self.breaks[self.crit_var[clause_idx]] -= 1
            self.num_true_lit[clause_idx] += 1

        for clause_idx in formula.get_occurrences(falsifying_literal):
            if self.num_true_lit[clause_idx] == 1:
                falselist.add(clause_idx)
                self.breaks[variable] -= 1
                self.crit_var[clause_idx] = variable
            elif self.num_true_lit[clause_idx] == 2:
                for lit in formula.clauses[clause_idx]:
                    if assignment.is_true(lit):
                        self.crit_var[clause_idx] = abs(lit)
                        self.increment_break_score(abs(lit))
            self.num_true_lit[clause_idx] -= 1
