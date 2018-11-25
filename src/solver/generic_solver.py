import time
import random

from src.formula import Formula, Assignment
from src.experiment.measurement import Measurement


class Context:
    """ Abstract Context Class;
    the generic SLS solver needs the given context constructor
    to construct an instance of this class or a subclass.
    """
    def update(self, flipped_var):
        raise Warning('Nothing implemented yet.')

    def is_sat(self):
        raise Warning('Nothing implemented yet.')


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
    measurement = measurement_constructor(formula, formula.num_vars // 2)

    t = 0
    while t < max_tries:

        # generate random assingnment
        if hamming_dist > 0:
            # if a hamming distance > 0 is given
            # flip 'hamming_dist' steps away from the satisfying assignment
            current_assignment = formula.satisfying_assignment
            for flip in rand_gen.sample(range(1,formula.num_vars+1), hamming_dist):
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
        assert isinstance(context,Context),\
            "context = {} :: {} is no Context".format(context, type(context))

        f = 0
        while f < max_flips:
            # check, if the current assignment is a solution
            if context.is_sat():
                measurement.end_run(success = True)
                return current_assignment, measurement

            # choose variable to flip
            to_flip = heuristic(context, rand_gen)

            # update context
            # also modifies 'current_assignment'
            context.update(to_flip)

            # register flip in measurement object
            measurement.count(to_flip)
            # increment flip counter
            f += 1

        measurement.end_run(success = False)
        # increment try counter
        t += 1

    # If no solution is found,
    # return None

    return None, measurement
