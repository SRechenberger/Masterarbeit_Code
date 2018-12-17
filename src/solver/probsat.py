import random
from src.solver.generic_solver import Context, generic_sls
from src.solver.walksat import DefensiveContext

def poly1(x,c):
    return pow(x,c)

def poly(br_score):
    return 1/(1+br_score)

breaks = []

def probsat_distribution(noise_param):
    def probsat_distr(context):
        global breaks
        if not breaks:
            breaks = [poly1(x,noise_param) for x in range(0,context.formula.max_occs+1)]

        get_break_score = context.score.get_break_score
        f = lambda i: poly(breaks[get_break_score(i)])
        distr = [0] * (context.formula.num_vars + 1)

        false_clauses = len(context.falselist)

        if false_clauses <= 0:
            distr[0] = 1

        clauses = context.formula.clauses
        for clause_idx in context.falselist:
            clause = clauses[clause_idx]
            score_sum = sum(map(f,map(abs,clause)))
            for var in map(abs, clause):
                # probability
                tmp = f(var)/score_sum
                # weighting
                distr[var] += tmp/false_clauses

        assert abs(sum(distr) - 1) < 0.0001,\
            "sum(distr) = {} != 1".format(sum(distr))

        return distr

    return probsat_distr


def probsat_heuristic(noise_param):
    assert type(noise_param) == float,\
        "noise_param = {} :: {} is no float".format(noise_param, type(noise_param))


    def heur(context, rand_gen=random):
        assert isinstance(context,DefensiveContext),\
            "context = {} :: {} is no GSATContext".format(context, type(context))

        global breaks
        if not breaks:
            breaks = [poly1(x,noise_param) for x in range(0,context.formula.max_occs+1)]

        f = lambda i: poly(breaks[context.score.get_break_score(i)])

        clause_idx = rand_gen.choice(context.falselist.lst)
        clause_vars = map(abs,context.formula.clauses[clause_idx])
        clause_score = list(map(f,clause_vars))
        score_sum = sum(clause_score)

        dice = rand_gen.random() * score_sum
        acc = 0
        for (i,s) in enumerate(clause_score):
            acc += s
            if dice < acc:
                return abs(context.formula.clauses[clause_idx][i])

        raise Warning("dice = {} i = {}".format(dice,i))

    return heur


def probsat(
        formula,
        measurement_constructor,
        max_tries,
        max_flips,
        noise_param=2.3,
        hamming_dist=0,
        rand_gen=random):
    return generic_sls(
        probsat_heuristic(noise_param),
        formula,
        max_tries,
        max_flips,
        DefensiveContext,
        measurement_constructor,
        hamming_dist=hamming_dist,
        rand_gen=rand_gen
    )

