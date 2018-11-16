import random
import numpy as np
from src.utils import *
from src.formula import Formula, Assignment
from src.solver.utils import Falselist, Scores
from src.solver.generic_solver import generic_sls, Context

class DefensiveContext(Context):
    def __init__(self, formula, assgn):
        assert isinstance(formula, Formula),\
            "formula = {} :: {} is no Formula".format(formula,type(formula))
        assert isinstance(assgn,Assignment),\
            "assgn = {} :: {} is no Assignment".format(assgn,type(assgn))

        self.formula = formula
        self.assgn = assgn
        self.variables = list(range(1,formula.num_vars+1))
        self.falselist = Falselist()
        self.score = Scores(self.formula, self.assgn, self.falselist)

    def update(self, flipped_var):
        assert type(flipped_var) == int,\
            "flipped_var = {} :: {} is no int".format(flipped_var, type(flipped_var))
        assert flipped_var > 0,\
            "flipped_var = {} <= 0".format(flipped_var)

        self.score.flip(
            flipped_var,
            self.formula,
            self.assgn,
            self.falselist
        )

    def is_sat(self):
        return len(self.falselist) == 0


def walksat_distribution(rho, context):
    assert isinstance(rho, float),\
        "rho = {} :: {} is not a float".format(rho, type(rho))

    # empty distribution
    distr = np.zeros(context.formula.num_vars + 1)

    # get number of false clauses to weight probabilities
    false_clauses = len(context.falselist)

    if false_clauses <= 0:
        distr[0] = 1

    for clause_idx in context.falselist:
        clause = context.formula.clauses[clause_idx]
        best_score = context.formula.max_occs
        clause_best = []

        for c in clause:
            v = abs(c)
            s = context.score.get_break_score(v)
            if s < best_score:
                best_score = s
                clause_best = [v]
            elif s == best_score:
                clause_best.append(v)

        if best_score == 0:
            for var in clause_best:
                distr[var] += 1/len(clause_best) * 1/false_clauses
        else:
            for var in map(abs,clause):
                # greedy and noisy step
                tmp = rho * 1/len(clause_best) + (1-rho) * 1/len(clause)
                # weighting
                distr[var] = tmp * 1/false_clauses

    assert sum(distr) == 1,\
        "sum(distr) = {} != 1".format(sum(distr))

    return distr


def walksat_heuristic(rho):
    if __debug__:
        type_check('rho',rho,float)

    def heur(context):
        if __debug__:
            instance_check('context',context,DefensiveContext)

        clause_idx = random.choice(context.falselist.lst)
        clause = context.formula.clauses[clause_idx]

        best_score = context.formula.max_occs
        clause_best = []

        for c in clause:
            v = abs(c)
            s = context.score.get_break_score(v)
            if s < best_score:
                best_score = s
                clause_best = [v]
            elif s == best_score:
                clause_best.append(v)


        # get random number [0,1)
        dice = random.random()
        # Greedy
        if best_score == 0 or dice > rho:
            return random.choice(list(clause_best))

        # Noisy
        else:
            return random.choice(list(map(abs,clause)))

    return heur


def walksat(formula, measurement, max_tries, max_flips, rho = 0.57):
    return generic_sls(
        walksat_heuristic(rho),
        formula,
        max_tries,
        max_flips,
        DefensiveContext,
        measurement
    )








