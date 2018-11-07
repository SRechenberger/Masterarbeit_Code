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
        GSATContext,
        measurement
    )








