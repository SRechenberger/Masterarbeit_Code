import re
import copy
import os
import sys
from src.utils import *
from src.formula import Formula, Assignment


class Falselist:
    """ Models a list with no need for order,
    for the list of unsatisfied clauses.
    """
    def __init__(self):
        self.lst = []
        self.mapping = {}

    def __iter__(self):
        return iter(self.lst)


    def remove(self, elem):
        assert elem in self.mapping

        idx = self.mapping[elem]
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


class DiffScores:

    def self_test(self, formula, assignment, falselist):
        """ Consistency test """

        # test num_true_lit
        for clause_idx, clause in enumerate(formula.clauses):
            true_lits = 0
            for lit in clause:
                true_lits += 1 if assignment.is_true(lit) else 0

            if true_lits != self.num_true_lit[clause_idx]:
                print(
                    "Clause {}: true_lits {} desired {}".format(
                        clause_idx, true_lits, self.num_true_lit[clause_idx]
                    )
                )
                return False

        # test variable scores
        for var in range(1,formula.num_vars+1):
            makes = 0
            breaks = 0
            sat_lit = var if assignment.get_value(var) else -var

            ## count make and break score
            # satisfying occurrences
            for clause_idx in formula.get_occurrences(sat_lit):
                if self.num_true_lit[clause_idx] == 1 and self.crit_var[clause_idx] == var:
                    breaks += 1

            # falsifying occurrences
            for clause_idx in formula.get_occurrences(-sat_lit):
                if self.num_true_lit[clause_idx] == 0:
                    makes += 1

            diff = (makes - breaks)
            if diff != self.get_score(var):
                print(
                    "Variable {}: make {} break {} diff {} desired {}".format(
                        var, makes, breaks, diff, self.get_score(var)
                    ),
                    file = sys.stderr,
                )
                return False

            if var not in self.buckets[self.get_score(var)]:
                return False

        # all good
        return True


    def __init__(self, formula, assignment, falselist):
        assert isinstance(formula,Formula), \
            "formula = {} :: {} is no Formula".format(formula,type(formula))
        assert isinstance(assignment,Assignment), \
            "assignment = {} :: {} is no Assignment".format(formula,type(assignment))
        assert isinstance(falselist,Falselist), \
            "falselist = {} :: {} is no Falselist".format(formula,type(falselist))

        self.max_score = formula.max_occs
        self.crit_var = []
        self.num_true_lit = []
        self.score = {}
        self.best_score = 0


        self.buckets = {
            k: set() for k in range(-formula.max_occs, formula.max_occs+1)
        }


        # all variables have score 0 and are in the 0-bucket
        for v in range(1,formula.num_vars+1):
            self.buckets[0].add(v)
            self.score[v] = 0


        # for each clause of the formula
        for clause_idx, clause in enumerate(formula.clauses):
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
                self.decrement_score(crit_var)

            # if there is no true literal
            elif self.num_true_lit[-1] == 0:
                # add the clause to the list of false clauses
                falselist.add(clause_idx)
                # a flip of any variable in the clause makes it sat
                for lit in clause:
                    self.increment_score(abs(lit))


    def get_best_bucket(self):
        """ Returns the first non-empty bucket """

        return self.best_score, self.buckets[self.best_score]



    def get_score(self, var):
        """ Returns the variable's break score """

        assert type(var) == int, "var = {} :: {} is no int".format(var, type(var))
        assert var > 0, "var = {} <= 0".format(var)

        return self.score[var]


    def increment_score(self, variable):
        """ Increments the score of the variable and lifts it into the next higher bucket """
        assert type(variable) == int, "variable = {} is no int".format(variable)
        assert variable > 0, "variable = {} <= 0".format(variable)

        # if the flipped variable has the best score,
        # and is lifted, then the best score is to be incremented
        if self.best_score == self.score[variable]:
            self.best_score += 1
        # lift variable to next higher bucket
        self.buckets[self.score[variable]].remove(variable)
        self.buckets[self.score[variable]+1].add(variable)
        # increment break score
        self.score[variable] += 1



    def decrement_score(self, variable):
        """ Decrements the score of the variable and lowers it into the next lower bucket """

        assert type(variable) == int, "variable = {} is no int".format(variable)
        assert variable > 0, "variable = {} <= 0".format(variable)


        # lower variable to next lower bucket
        self.buckets[self.score[variable]].remove(variable)
        # if the flipped variable was the only variable with best score, and is lowered
        # then the best score is lowered
        if self.best_score == self.score[variable] and not self.buckets[self.score[variable]]:
            self.best_score -= 1
        self.buckets[self.score[variable]-1].add(variable)
        # decrement break score
        self.score[variable] -= 1


    def flip(self, variable, formula, assignment, falselist):
        assert type(variable) == int, \
            "variable = {} :: {} is no int".format(variable, type(variable))
        assert variable > 0, "variable = {} <= 0".format(variable)
        assert isinstance(formula,Formula), \
            "formula = {} :: {} is no Formula".format(formula,type(formula))
        assert isinstance(assignment,Assignment), \
            "assignment = {} :: {} is no Assignment".format(formula,type(assignment))
        assert isinstance(falselist,Falselist), \
            "falselist = {} :: {} is no Falselist".format(formula,type(falselist))

        # a[v] = -a[v]
        assignment.flip(variable) # TODO this does not really belong here
        # satisfyingLiteral = a[v] ? v : -v
        satisfying_literal = variable if assignment.is_true(variable) else -variable
        # falsifyingLiteral = a[v] ? -v : v
        falsifying_literal = -variable if assignment.is_true(variable) else variable
        # for each clause, 'satisfyingLiteral' occurs in
        for clause_idx in formula.get_occurrences(satisfying_literal):
            # if the clause is unsat
            if self.num_true_lit[clause_idx] == 0:
                # remove from falselist
                falselist.remove(clause_idx)
                # no literal in the clause makes it sat anymore (for it is now sat),
                # but 'variable' would break it,
                # therefore, its score is decremented twice
                self.decrement_score(variable)
                for lit in formula.clauses[clause_idx]:
                    self.decrement_score(abs(lit))
                # make 'variable' critical (for it is now the only satisfying variable)
                self.crit_var[clause_idx] = variable

            # if the clause is sat by one literal
            elif self.num_true_lit[clause_idx] == 1:
                # the clauses critical variable does no longer break it
                # i.e. it isn't critical anymore
                self.increment_score(self.crit_var[clause_idx])

            # the clause has one more satisfying literal
            self.num_true_lit[clause_idx] += 1

        # for each clause, 'falsifying_literal' occurs in
        for clause_idx in formula.get_occurrences(falsifying_literal):
            # if the variable was critical
            if self.num_true_lit[clause_idx] == 1:
                # add the clause to the falselist
                falselist.add(clause_idx)
                # 'variable' now no longer breaks the clause, but would make it;
                # thus its score is incremented twice
                # the score of all other variables will be increased
                self.increment_score(variable)
                for lit in formula.clauses[clause_idx]:
                    self.increment_score(abs(lit))
                # set variable as critical (for whatever reason)
                self.crit_var[clause_idx] = variable

            # if the clause was satisfyed by a second variable
            elif self.num_true_lit[clause_idx] == 2:
                # find the critical variable
                for lit in formula.clauses[clause_idx]:
                    # if the literal satisfies the clause
                    if assignment.is_true(lit):
                        # make it the critical variable
                        self.crit_var[clause_idx] = abs(lit)
                        # increment its break score
                        self.decrement_score(abs(lit))

            # the clause is now satisfied by one fewer literal
            self.num_true_lit[clause_idx] -= 1


class Scores:
    def self_test(self, formula, assignment, falselist):
        """ Consistency test """

        # test num_true_lit
        for clause_idx, clause in enumerate(formula.clauses):
            true_lits = 0
            for lit in clause:
                true_lits += 1 if assignment.is_true(lit) else 0

            if true_lits != self.num_true_lit[clause_idx]:
                print(
                    "Clause {}: true_lits {} desired {}".format(
                        clause_idx, true_lits, self.num_true_lit[clause_idx]
                    )
                )
                return False

        # test variable scores
        for var in range(1,formula.num_vars+1):
            breaks = 0
            sat_lit = var if assignment.get_value(var) else -var

            ## count make and break score
            # satisfying occurrences
            for clause_idx in formula.get_occurrences(sat_lit):
                if self.num_true_lit[clause_idx] == 1 and self.crit_var[clause_idx] == var:
                    breaks += 1

            if breaks != self.get_break_score(var):
                print(
                    "Variable {}: break {} desired {}".format(
                        var, breaks, self.get_score(var)
                    ),
                    file = sys.stderr,
                )
                return False

            if var not in self.buckets[self.get_break_score(var)]:
                return False

        # all good
        return True


    def __init__(self, formula, assignment, falselist):
        assert isinstance(formula,Formula), \
            "formula = {} :: {} is no Formula".format(formula,type(formula))
        assert isinstance(assignment,Assignment), \
            "assignment = {} :: {} is no Assignment".format(formula,type(assignment))
        assert isinstance(falselist,Falselist), \
            "falselist = {} :: {} is no Falselist".format(formula,type(falselist))


        self.formula = formula
        self.crit_var = [
            0 for _ in formula.clauses
        ]
        self.num_true_lit = [
            0 for _ in formula.clauses
        ]
        self.breaks = {}

        self.buckets = [
            set() for _ in range(0, formula.max_occs+1) # formula.max_occs+1)
        ]
        self.best_score = 0


        # all variables have score 0 and are in the 0-bucket
        for v in range(1,formula.num_vars+1):
            self.buckets[0].add(v)
            self.breaks[v] = 0

        # for each clause of the formula
        for clause_idx, clause in enumerate(formula.clauses):
            # a local variable to track the critical variable
            crit_var = 0
            # for each literal of the clause
            for lit in clause:
                # if the literal is satisfied
                if assignment.is_true(lit):
                    # it MAY BE the critical variable of the clause
                    crit_var = abs(lit)
                    # there is one more true literal
                    self.num_true_lit[clause_idx] += 1

            # if after the traverse of the clause there is exactly one true
            # literal
            if self.num_true_lit[clause_idx] == 1:
                # it is the critical literal
                self.crit_var[clause_idx] = crit_var
                # thus it breaks the clause
                self.increment_break_score(crit_var)

            # if there is no true literal
            elif self.num_true_lit[clause_idx] == 0:
                # add the clause to the list of false clauses
                falselist.add(clause_idx)


    def get_best_bucket(self):
        """ Returns the first non-empty bucket """
        for score, bucket in enumerate(self.buckets):
            if bucket:
                return score, bucket

        raise RuntimeError("all buckets are empty")


    def get_break_score(self, var):
        """ Returns the variable's break score """

        assert type(var) == int, "var = {} :: {} is no int".format(var, type(var))
        assert var > 0, "var = {} <= 0".format(var)

        return self.breaks[var]


    def increment_break_score(self, variable):
        """ Increments the Break score of the variable and lifts it into the next higher bucket """

        assert type(variable) == int, "variable = {} is no int".format(variable)
        assert variable > 0, "variable = {} <= 0".format(variable)

        # remove variable from old bucket
        self.buckets[self.breaks[variable]].remove(variable)
        if self.best_score == self.breaks[variable] and not self.buckets[self.breaks[variable]]:
            self.best_score += 1
        # increment break score
        self.breaks[variable] += 1
        # add variable to new bucket
        self.buckets[self.breaks[variable]].add(variable)


    def decrement_break_score(self, variable):
        """ Decrements the Break score of the variable and lowers it into the next lower bucket """

        assert type(variable) == int, "variable = {} is no int".format(variable)
        assert variable > 0, "variable = {} <= 0".format(variable)
        assert variable in self.breaks, "variable = {} not listed in self.breaks".format(variable)

        if self.best_score == self.breaks[variable]:
            self.best_score -= 1
        # remove variable from old bucket
        self.buckets[self.breaks[variable]].remove(variable)
        # decrement break score
        self.breaks[variable] -= 1
        # add variable to new bucket
        self.buckets[self.breaks[variable]].add(variable)

        assert self.breaks[variable] >= 0, "self.breaks[variable] = {} < 0".format(self.breaks[variable])


    def flip(self, variable, formula, assignment, falselist):
        assert type(variable) == int, \
            "variable = {} :: {} is no int".format(variable, type(variable))
        assert variable > 0, "variable = {} <= 0".format(variable)
        assert isinstance(formula,Formula), \
            "formula = {} :: {} is no Formula".format(formula,type(formula))
        assert isinstance(assignment,Assignment), \
            "assignment = {} :: {} is no Assignment".format(formula,type(assignment))
        assert isinstance(falselist,Falselist), \
            "falselist = {} :: {} is no Falselist".format(formula,type(falselist))

        # a[v] = -a[v]
        assignment.flip(variable)
        # satisfyingLiteral = a[v] ? v : -v
        satisfying_literal = variable if assignment.is_true(variable) else -variable
        # falsifyingLiteral = a[v] ? -v : v
        falsifying_literal = -variable if assignment.is_true(variable) else variable
        # for each clause, 'satisfyingLiteral' occurs in
        for clause_idx in formula.get_occurrences(satisfying_literal):
            assert satisfying_literal in formula.clauses[clause_idx], \
                "literal {} not in clause {}#{}".format(
                    satisfying_literal, clause_idx, formula.clauses[clause_idx]
                )
            # if the clause is unsat
            if self.num_true_lit[clause_idx] == 0:
                # remove from falselist
                falselist.remove(clause_idx)
                # increment break score of 'variable'
                self.increment_break_score(variable)    # TODO this line triggers the error
                # make 'variable' critical (dito)
                self.crit_var[clause_idx] = variable

            # if the clause is sat by one literal
            elif self.num_true_lit[clause_idx] == 1:
                # 'variable' does not break it
                self.decrement_break_score(self.crit_var[clause_idx])

            # the clause has one more satisfying literal
            self.num_true_lit[clause_idx] += 1

        # for each clause, 'falsifying_literal' occurs in
        for clause_idx in formula.get_occurrences(falsifying_literal):
            assert falsifying_literal in formula.clauses[clause_idx], \
                "literal {} not in clause {}#{}".format(
                    falsifying_literal, clause_idx, formula.clauses[clause_idx]
                )
            # if the variable was critical
            if self.num_true_lit[clause_idx] == 1:
                # add the clause to the falselist
                falselist.add(clause_idx)
                # decrement its break score (for the clause is already broken)
                self.decrement_break_score(variable)
                # set variable as critical (for whatever reason)
                self.crit_var[clause_idx] = variable

            # if the clause was satisfyed by a second variable
            elif self.num_true_lit[clause_idx] == 2:
                # find the critical variable
                for lit in formula.clauses[clause_idx]:
                    # if the literal satisfies the clause
                    if assignment.is_true(lit):
                        # make it the critical variable
                        self.crit_var[clause_idx] = abs(lit)
                        # increment its break score
                        self.increment_break_score(abs(lit))

            # the clause is now satisfied by one fewer literal
            self.num_true_lit[clause_idx] -= 1
