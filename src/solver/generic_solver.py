"""
## Module src.solver.generic_solver

### Contents
    - class Context
    - function generic_sls

"""

import random

from src.formula import Formula, Assignment
from src.solver.utils import Falselist

class Context:
    """ Context for GSAT, WalkSAT and ProbSAT solvers """

    def __init__(self, score_constr, formula, assgn):
        assert isinstance(formula, Formula),\
            "formula = {} :: {} is no Formula".format(formula, type(formula))
        assert isinstance(assgn, Assignment),\
            "assgn = {} :: {} is no Assignment".format(assgn, type(assgn))

        self.formula = formula
        self.assgn = assgn
        self.variables = list(range(1, formula.num_vars+1))
        self.falselist = Falselist()
        self.score = score_constr(self.formula, self.assgn, self.falselist)

    def update(self, flipped_var):
        """ Update context after flip.

        Positionals:
            flipped_var -- the flipped variable
        """

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
        """ Check if the formula should be satisfied by the current assignment """

        return len(self.falselist) == 0


def generic_sls(
        heuristic,
        formula,
        max_tries,
        max_flips,
        context_constructor,
        measurement_constructor,
        hamming_dist=0,
        rand_gen=random):
    """ Generic SLS-Solver according to Algorithm 1,
    including measurement facilities.
    """

    assert callable(heuristic),\
        "heuristic = {} :: {} is not callable".format(heuristic, type(heuristic))
    assert isinstance(formula, Formula),\
        "formula = {} :: {} is no formula".format(formula, type(formula))
    assert isinstance(max_tries, int),\
        "max_tries = {} :: {} is no int".format(max_tries, type(max_tries))
    assert max_tries > 0,\
        "max_tries = {} <= 0".format(max_tries)
    assert isinstance(max_flips, int),\
        "max_flips = {} :: {} is no int".format(max_flips, type(max_flips))
    assert max_flips > 0,\
        "max_flips = {} <= 0".format(max_flips)
    assert callable(context_constructor),\
        "context_constructor = {} :: {} is not callable"


    #initialize measurement object
    measurement = measurement_constructor(formula, formula.num_vars)

    for _ in range(max_tries):
        # generate random assingnment
        if hamming_dist > 0:
            # if a hamming distance > 0 is given
            # flip 'hamming_dist' steps away from the satisfying assignment
            current_assignment = formula.satisfying_assignment
            for flip in rand_gen.sample(range(1, formula.num_vars+1), hamming_dist):
                current_assignment.flip(flip)
        else:
            # otherwise generate a random one
            current_assignment = Assignment.generate_random_assignment(
                formula.num_vars,
                rand_gen
            )
        # setup measurement object for a search run
        measurement.init_run(current_assignment)

        # initialize context
        context = context_constructor(formula, current_assignment)
        assert hasattr(context, 'update') and callable(context.update),\
            "context = {} has no method update"
        assert hasattr(context, 'is_sat') and callable(context.is_sat),\
            "context = {} has no method is_sat"

        for _ in range(max_flips):
            # check, if the current assignment is a solution
            if context.is_sat():
                measurement.end_run(success=True)
                return current_assignment, measurement

            # choose variable to flip
            to_flip = heuristic(context, rand_gen)

            # update context
            # also modifies 'current_assignment'
            context.update(to_flip)

            # register flip in measurement object
            measurement.count(to_flip)

        measurement.end_run(success=False)

    # If no solution is found,
    # return None

    return None, measurement
