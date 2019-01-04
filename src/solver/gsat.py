"""
## Module src.solver.gsat

### Contents
    - function gsat_distribution
    - function gsat_heuristic
    - function gsat
"""

import random

from functools import partial

from src.solver.generic_solver import generic_sls, Context
from src.solver.utils import DiffScores


def gsat_distribution(noise_param=0):
    """ Constructs a function, returning the specific distribution of the GSAT heuristic.

    Keywords:
        noise_param -- only for compatibility; will be ignored

    Returns:
        dist -- function return a probability distribution, given a context value
    """

    def dist(context):
        """ Returns the specific probability distribution for the GSAT heuristic,
        given a context.

        Positionals:
            context -- context to calculate the distribution from

        Returns:
            distr -- list, where distr[i] is the probability of variable i to be flipped
        """

        # begin with an empty distribution
        distr = [0] * (context.formula.num_vars + 1)

        _, best = context.score.get_best_bucket()
        for i in best:
            distr[i] = 1/len(best)

        assert abs(sum(distr) - 1) < 0.001,\
            "sub(distr) = {} != 1".format(sum(distr))

        return distr

    return dist


def gsat_heuristic(noise_param=0):
    """ Constructs the GSAT heuristik.

    Keywords:
        noise_param -- only for compatibility; will be ignored

    Returns:
        heur -- function, choosing a variable to be flipped.
    """
    def heur(context, rand_gen=random):
        """ The GSAT heuristic.

        Positionals:
            context -- context of the current search state

        Returns:
            var -- variable to be flipped
        """
        _, best = context.score.get_best_bucket()
        return rand_gen.choice(list(best))

    return heur


def gsat(
        formula,
        measurement_constructor,
        max_tries, max_flips,
        noise_param=0,              # will be ignored
        hamming_dist=0,
        rand_gen=random):

    """ GSAT Solver.

    Positionals:
        formula -- formula, for which to find a satisfying assignment
        measurement_constructor -- constructor for a measurement object
        max_tries -- maximum number of tries, before unsucessful termination
        max_flips -- maximum number of flips, before starting a new search

    Keywords:
        noise_param -- only for compatibility; will be ignored
        hamming_dist -- force random assignment to be at a certain hamming distance
                        to the known satsifying one.
        rand_gen -- random number generator
    """

    return generic_sls(
        gsat_heuristic(noise_param=noise_param),
        formula,
        max_tries,
        max_flips,
        partial(Context, DiffScores),
        measurement_constructor,
        hamming_dist=hamming_dist,
        rand_gen=rand_gen,
    )
