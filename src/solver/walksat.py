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


def walksat_distribution(rho):
    assert isinstance(rho, float),\
        "rho = {} :: {} is not a float".format(rho, type(rho))

    def walksat_distr(context):
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
                    greedy = (1-rho)/len(clause_best) if var in clause_best else 0
                    noisy = rho/len(clause)
                    # weighting
                    distr[var] += (greedy + noisy)/false_clauses

        assert abs(sum(distr) - 1) < 0.001,\
            "sum(distr) = {} != 1".format(sum(distr))

        return distr

    return walksat_distr


def walksat_heuristic(rho):
    assert isinstance(rho, float),\
        "rho = {} :: {} is not a float".format(rho, type(rho))

    def heur(context, rand_gen=random):
        assert isinstance(context, DefensiveContext),\
            "context = {} :: {} is no DefensiveContext"

        clause_idx = rand_gen.choice(context.falselist.lst)
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
        dice = rand_gen.random()
        # Greedy
        if best_score == 0 or dice > rho:
            return rand_gen.choice(list(clause_best))

        # Noisy
        else:
            return rand_gen.choice(list(map(abs,clause)))

    return heur


def walksat(formula, measurement_constructor, max_tries, max_flips, rho = 0.57, hamming_dist=0, rand_gen=random):

    return generic_sls(
        walksat_heuristic(rho),
        formula,
        max_tries,
        max_flips,
        DefensiveContext,
        measurement_constructor,
        hamming_dist=hamming_dist,
        rand_gen=rand_gen
    )
