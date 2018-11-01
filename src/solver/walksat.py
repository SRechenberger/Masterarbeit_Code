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
            best = context.score.get_best_bucket()
            return random.choice(list(best))

        # Noisy
        else:
            return random.choice(list(map(abs,clause)))

    return heur

def walksat(formula, max_tries, max_flips, measurement, rho = 0.57):
    return generic_sls(
        walksat_heuristic(rho),
        formula,
        max_tries,
        max_flips,
        GSATContext,
        measurement
    )








