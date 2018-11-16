import numpy as np
from src.solver.generic_solver import Context, generic_sls
from src.solver.utils import DiffScores, Scores, Falselist
from src.formula import Formula, Assignment
from collections.abc import Sequence
import random
from src.utils import *

import sys

class GSATContext(Context):
    def __init__(self, formula, assgn):
        if __debug__:
            instance_check('formula', formula, Formula)
            instance_check('assgn', assgn, Assignment)

        self.formula = formula
        self.variables = list(range(1,formula.num_vars+1))
        self.assgn = assgn
        self.falselist = Falselist()
        self.score = DiffScores(formula, assgn, self.falselist)

    def update(self, flipped_var):
        if __debug__:
            type_check('flipped_var', flipped_var, int)
            value_check(
                'flipped_var', flipped_var,
                strict_pos = strict_positive
            )

        self.score.flip(
            flipped_var,
            self.formula,
            self.assgn,
            self.falselist
        )

    def is_sat(self):
        return len(self.falselist) == 0


def max_seq(seq, key=lambda x:x):
    if __debug__:
        instance_check('seq',seq,Sequence)
        value_check('seq',seq,non_empty = lambda x: len(x) != 0)

    max_seq = [seq[0]]
    max_val = key(seq[0])
    for x in seq[1:]:
        if key(x) > max_val:
            max_seq = [x]
            max_val = key(x)

        elif key(x) == max_val:
            max_seq.append(x)

    return max_seq


def gsat_distribution(context):
    # begin with an empty distribution
    distr = np.zeros(context.formula.num_vars + 1)

    _, best = context.score.get_best_bucket()
    for i in best:
        distr[i] = 1/len(best)

    assert sum(distr) == 1,\
        "sub(distr) = {} != 1".format(sum(distr))

    return distr


def gsat_heuristic(context):
    score, best = context.score.get_best_bucket()

    return random.choice(list(best))


def gsat(formula, measurement, max_tries, max_flips):
    return generic_sls(
        gsat_heuristic,
        formula,
        max_tries,
        max_flips,
        GSATContext,
        measurement
    )
