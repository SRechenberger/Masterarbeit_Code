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
        self.variables = set(range(1,formula.num_vars+1))
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


def gsat_heuristic(context):
    """ Sucks complexitywise; needs to be somehow constant in |Var(F)| """
    max_set = []
    max_score = -context.formula.num_clauses
    vs = context.variables
    for v in vs:
        score = context.score.get_make_score(v) - context.score.get_break_score(v)
        if score > max_score:
            max_score = score
            max_set = [v]

        elif score == max_score:
            max_set.append(v)

    return random.choice(max_set)

def gsat(formula, max_tries, max_flips, measurement):
    return generic_sls(
        gsat_heuristic,
        formula,
        max_tries,
        max_flips,
        GSATContext,
        measurement
    )
