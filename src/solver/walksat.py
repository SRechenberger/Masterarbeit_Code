"""
## Module src.solver.walksat

### Contents
    - function walksat_distribution
    - function walksat_heuristic
    - function walksat
"""

import random
import operator

from functools import partial

from src.solver.utils import Scores, max_seq
from src.solver.generic_solver import generic_sls, Context


def walksat_distribution(noise_param):
    """ Constructs a function, returning the specific distribution of the WalkSAT heuristic.

    Positionals:
        noise_param -- parameter rho for WalkSAT; should hold 0 <= rho <= 1

    Returns:
        dist -- function return a probability distribution, given a context value
    """

    assert isinstance(noise_param, float),\
        "noise_param = {} :: {} is not a float".format(noise_param, type(noise_param))
    assert 0 <= noise_param <= 1,\
        "noise_param = {} not in [0,1]"

    def dist(context):
        """ Returns the specific probability distribution for the WalkSAT heuristic,
        given a context.

        Positionals:
            context -- context to calculate the distribution from

        Returns:
            distr -- list, where distr[i] is the probability of variable i to be flipped
        """
        # empty distribution
        distr = [0] * (context.formula.num_vars + 1)

        # get number of false clauses to weight probabilities
        false_clauses = len(context.falselist)

        if false_clauses <= 0:
            distr[0] = 1

        for clause_idx in context.falselist:
            clause = context.formula.clauses[clause_idx]

            best_score, clause_best = max_seq(
                clause,
                key=context.score.get_break_score,
                compare=operator.lt,
                modifier=abs,
            )

            if best_score == 0:
                for var in clause_best:
                    distr[var] += 1/len(clause_best) * 1/false_clauses
            else:
                for var in map(abs, clause):
                    # greedy and noisy step
                    greedy = (1-noise_param)/len(clause_best) if var in clause_best else 0
                    noisy = noise_param/len(clause)
                    # weighting
                    distr[var] += (greedy + noisy)/false_clauses

        assert abs(sum(distr) - 1) < 0.001,\
            "sum(distr) = {} != 1".format(sum(distr))

        return distr

    return dist


def walksat_heuristic(noise_param):
    """ Constructs the WalkSAT heuristik.

    Positionals:
        noise_param -- parameter rho for WalkSAT; should hold 0 <= rho <= 1

    Returns:
        heur -- function, choosing a variable to be flipped.
    """
    assert isinstance(noise_param, float),\
        "noise_param = {} :: {} is not a float".format(noise_param, type(noise_param))
    assert 0 <= noise_param <= 1,\
        "noise_param = {} should not in [0,1]"

    def heur(context, rand_gen=random):
        """ The WalkSAT heuristic.

        Positionals:
            context -- context of the current search state

        Returns:
            var -- variable to be flipped
        """

        clause_idx = rand_gen.choice(context.falselist.lst)
        clause = context.formula.clauses[clause_idx]

        best_score, clause_best = max_seq(
            clause,
            key=context.score.get_break_score,
            compare=operator.lt,
            modifier=abs,
        )

        # get random number [0,1)
        dice = rand_gen.random()
        # Greedy
        if best_score == 0 or dice > noise_param:
            return abs(rand_gen.choice(list(clause_best)))

        # Noisy
        return rand_gen.choice(list(map(abs, clause)))

    return heur


def walksat(
        formula,
        measurement_constructor,
        max_tries,
        max_flips,
        noise_param=0.57,
        hamming_dist=0,
        rand_gen=random):
    """ WalkSAT Solver.

    Positionals:
        formula -- formula, for which to find a satisfying assignment
        measurement_constructor -- constructor for a measurement object
        max_tries -- maximum number of tries, before unsucessful termination
        max_flips -- maximum number of flips, before starting a new search

    Keywords:
        noise_param -- parameter rho for WalkSAT; should hold 0 <= rho <= 1
        hamming_dist -- force random assignment to be at a certain hamming distance
                        to the known satsifying one.
        rand_gen -- random number generator
    """

    return generic_sls(
        walksat_heuristic(noise_param),
        formula,
        max_tries,
        max_flips,
        partial(Context, Scores),
        measurement_constructor,
        hamming_dist=hamming_dist,
        rand_gen=rand_gen
    )
