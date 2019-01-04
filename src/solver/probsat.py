"""
## Module src.solver.probsat

### Contents
    - function probsat_distribution
    - function probsat_heuristic
    - function probsat
"""

import random

from functools import partial

from src.solver.generic_solver import generic_sls, Context
from src.solver.utils import Scores

def poly(br_score):
    """ Calculate weighted break score """
    return 1/(1+br_score)

BREAKS = []

def probsat_distribution(noise_param):
    """ Constructs a function, returning the specific distribution of the ProbSAT heuristic.

    Positionals:
        noise_param -- parameter cb for ProbSAT; should hold 0 <= cb

    Returns:
        dist -- function return a probability distribution, given a context value
    """

    assert isinstance(noise_param, float),\
        "noise_param = {} :: {} is not a float".format(noise_param, type(noise_param))
    assert 0 <= noise_param,\
        "noise_param = {} < 0"

    def probsat_distr(context):
        """ Returns the specific probability distribution for the ProbSAT heuristic,
        given a context.

        Positionals:
            context -- context to calculate the distribution from

        Returns:
            distr -- list, where distr[i] is the probability of variable i to be flipped
        """

        global BREAKS
        if not BREAKS:
            BREAKS = [pow(x, noise_param) for x in range(0, context.formula.max_occs*2)]

        get_break_score = context.score.get_break_score
        f = lambda i: poly(BREAKS[get_break_score(i)])
        distr = [0] * (context.formula.num_vars + 1)

        false_clauses = len(context.falselist)

        if false_clauses <= 0:
            distr[0] = 1

        clauses = context.formula.clauses
        for clause_idx in context.falselist:
            clause = clauses[clause_idx]
            score_sum = sum(map(f, map(abs, clause)))
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
    """ Constructs the ProbSAT heuristik.

    Positionals:
        noise_param -- parameter cb for ProbSAT; should hold 0 <= cb

    Returns:
        heur -- function, choosing a variable to be flipped.
    """

    assert isinstance(noise_param, float),\
        "noise_param = {} :: {} is no float".format(noise_param, type(noise_param))
    assert 0 <= noise_param,\
        "noise_param = {} < 0"

    def heur(context, rand_gen=random):
        """ The ProbSAT heuristic.

        Positionals:
            context -- context of the current search state

        Returns:
            var -- variable to be flipped
        """

        global BREAKS
        if not BREAKS:
            BREAKS = [pow(x, noise_param) for x in range(0, context.formula.max_occs*2)]

        get_break_score = context.score.get_break_score
        f = lambda i: poly(BREAKS[get_break_score(i)])

        clause_idx = rand_gen.choice(context.falselist.lst)
        clause_vars = map(abs, context.formula.clauses[clause_idx])
        clause_score = list(map(f, clause_vars))
        score_sum = sum(clause_score)

        dice = rand_gen.random() * score_sum
        acc = 0
        for (i, s) in enumerate(clause_score):
            acc += s
            if dice < acc:
                return abs(context.formula.clauses[clause_idx][i])

        raise RuntimeError("No variable chosen")

    return heur


def probsat(
        formula,
        measurement_constructor,
        max_tries,
        max_flips,
        noise_param=2.3,
        hamming_dist=0,
        rand_gen=random):
    """ ProbSAT Solver.

    Positionals:
        formula -- formula, for which to find a satisfying assignment
        measurement_constructor -- constructor for a measurement object
        max_tries -- maximum number of tries, before unsucessful termination
        max_flips -- maximum number of flips, before starting a new search

    Keywords:
        noise_param -- parameter cb for ProbSAT; should hold 0 <= cb
        hamming_dist -- force random assignment to be at a certain hamming distance
                        to the known satsifying one.
        rand_gen -- random number generator
    """
    return generic_sls(
        probsat_heuristic(noise_param),
        formula,
        max_tries,
        max_flips,
        partial(Context, Scores),
        measurement_constructor,
        hamming_dist=hamming_dist,
        rand_gen=rand_gen
    )
