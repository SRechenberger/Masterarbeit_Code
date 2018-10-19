from src.solver.generic_solver import Context, generic_sls
from src.solver.gsat import GSATContext
import random
from src.utils import *

def poly1(x,c):
    return pow(x,c)

def poly(mk_score,br_score):
    return mk_score/(1+br_score)

def exp1(x,c):
    return pow(c,x)

def exp(mk_score,br_score):
    return mk_score/br_score


functions = dict(
    poly = (poly1,poly),
    exp = (exp1,exp)
)

def probsat_heuristic(max_occ,c_make,c_break,func_lbl = 'poly'):
    if __debug__:
        type_check('c_make',c_make,float)
        type_check('c_break',c_break,float)
        value_check(
            'func_lbl',func_lbl,
            either_poly_or_exp = lambda f: f == 'poly' or f == 'exp'
        )

    func1, func = functions[func_lbl]

    makes  = [func1(x,c_make)  for x in range(0,max_occ+1)]
    breaks = [func1(x,c_break) for x in range(0,max_occ+1)]

    def heur(context):
        if __debug__:
            instance_check('context',context,GSATContext)

        f = lambda i: func(
            makes[context.score.get_make_score(i)],
            breaks[context.score.get_break_score(i)]
        )

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

def probsat(c_make,c_break,func,formula,max_tries,max_flips,measurement):
    return generic_sls(
        probsat_heuristic(formula.max_occs,c_make,c_break,func),
        formula,
        max_tries,
        max_flips,
        GSATContext,
        measurement
    )

