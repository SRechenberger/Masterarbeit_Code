import random
import sys

from src.solver.generic_solver import Context, generic_sls
from src.solver.utils import DiffScores, Scores, Falselist
from src.formula import Formula, Assignment


class GSATContext(Context):
    def __init__(self, formula, assgn):
        assert isinstance(formula, Formula),\
            "formula = {} :: {} is no Formula".format(formula, type(formula))
        assert isinstance(assgn, Assignment),\
            "assgn = {} :: {} is no Assignment".format(assgn, type(assgn))

        self.formula = formula
        self.variables = list(range(1,formula.num_vars+1))
        self.assgn = assgn
        self.falselist = Falselist()
        self.score = DiffScores(formula, assgn, self.falselist)

    def update(self, flipped_var):
        assert isinstance(flipped_var, int),\
            "flipped_var = {} :: {} is no int".format(flipped_var, type(flipped_var))
        assert flipped_var > 0,\
            "flipped_var = {} <= 0".format(flipped_var)

        self.score.flip(
            flipped_var,
            self.formula,
            self.assgn,
            self.falselist
        )

    def is_sat(self):
        return len(self.falselist) == 0

def gsat_distribution(noise_param=0):
    def dist(context):
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
    def heur(context, rand_gen=random):
        score, best = context.score.get_best_bucket()
        return rand_gen.choice(list(best))

    return heur


def gsat(
        formula,
        measurement_constructor,
        max_tries, max_flips,
        noise_param=0,              # will be ignored
        hamming_dist=0,
        rand_gen=random):
    return generic_sls(
        gsat_heuristic(noise_param=noise_param),
        formula,
        max_tries,
        max_flips,
        GSATContext,
        measurement_constructor,
        hamming_dist=hamming_dist,
        rand_gen=rand_gen,
    )
