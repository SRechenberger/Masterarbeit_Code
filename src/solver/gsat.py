from collections.abc import Sequence
from src.solver.generic_solver import Measurement, Context, generic_sls
from src.solver.utils import Formula, Assignment, Scores, Falselist
import random
from src.utils import *

class GSATContext(Context):
    def __init__(self, formula, assgn):
        if __debug__:
            instance_check('formula', formula, Formula)
            instance_check('assgn', assgn, Assignment)

        self.formula = formula
        self.variables = list(range(1,formula.num_vars+1))
        self.assgn = assgn
        self.falselist = Falselist()
        self.score = Scores(formula, assgn, self.falselist)

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


def gsat_heuristic(context):
    """ Sucks complexitywise; needs to be somehow constant in |Var(F)| """

    best = max_seq(
        context.variables,
        key = lambda v: context.score.get_make_score(v) - context.score.get_break_score(v)
    )

    return random.choice(best)

def gsat(formula, max_tries, max_flips, measurement):
    return generic_sls(
        gsat_heuristic,
        formula,
        max_tries,
        max_flips,
        GSATContext,
        measurement
    )
