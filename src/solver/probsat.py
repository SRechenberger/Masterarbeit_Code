from src.solver.generic_solver import Context, generic_sls
from src.solver.gsat import GSATContext
import random
from src.utils import *

def poly1(x,c):
    return pow(x,c)

def poly(br_score):
    return 1/(1+br_score)

def exp1(x,c):
    return pow(c,x)

def exp(br_score):
    return 1/br_score


functions = dict(
    poly = (poly1,poly),
    exp = (exp1,exp)
)

def probsat_heuristic(max_occ, c_break, phi = 'poly'):
    assert type(c_break) == float, "c_break = {} :: {} is no float".format(c_break, type(c_break))
    assert type(phi) == str, "phi = {} :: {} is no str".format(phi, type(phi))
    assert phi in functions, "phi = {} is not in {}".format(phi, list(functions.keys()))

    func1, func = functions[phi]

    breaks = [func1(x,c_break) for x in range(0,max_occ+1)]

    def heur(context):
        assert isinstance(context,GSATContext), "context = {} :: {} is no GSATContext".format(context, type(context))

        f = lambda i: func(breaks[context.score.get_break_score(i)])

        clause_idx = random.choice(context.falselist.lst)
        clause_vars = map(abs,context.formula.clauses[clause_idx])
        clause_score = list(map(f,clause_vars))
        score_sum = sum(clause_score)

        dice = random.random() * score_sum
        acc = 0
        for (i,s) in enumerate(clause_score):
            acc += s
            if dice < acc:
                return abs(context.formula.clauses[clause_idx][i])

        raise Warning("dice = {} i = {}".format(dice,i))

    return heur

def probsat(formula, measurement, max_tries, max_flips, c_break = 2.3, phi = 'poly'):
    return generic_sls(
        probsat_heuristic(formula.max_occs,c_break,phi),
        formula,
        max_tries,
        max_flips,
        GSATContext,
        measurement
    )

