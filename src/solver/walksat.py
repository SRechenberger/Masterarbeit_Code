from src.solver.gsat import GSATContext, max_seq
from src.solver.generic_solver import generic_sls
import random
from src.utils import *

def walksat_heuristic(rho):
    if __debug__:
        type_check('rho',rho,float)

    def heur(context):
        if __debug__:
            instance_check('context',context,GSATContext)

        clause_idx = random.choice(context.falselist.lst)
        clause = context.formula.clauses[clause_idx]
        dice = random.random()

        # Greedy
        if dice < rho:
            best_vars = max_seq(
                list(map(abs,clause)),
                key = lambda v: context.score.get_make_score(v) - context.score.get_break_score(v)
            )
            return random.choice(best_vars)

        # Noisy
        else:
            return random.choice(list(map(abs,clause)))

    return heur

def walksat(rho, formula, max_tries, max_flips, measurement):
    return generic_sls(
        walksat_heuristic(rho),
        formula,
        max_tries,
        max_flips,
        GSATContext,
        measurement
    )








