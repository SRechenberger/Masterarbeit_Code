import time
import random

from src.formula import Formula, Assignment
from src.experiment.measurement import Measurement
from src.utils import *


debug = False

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

    if __debug__:
        value_check(
            'heuristic',heuristic,
            is_callable = callable,
            arity_1     = has_arity(1)
        )
        instance_check('formula',formula,Formula)
        type_check('max_tries',max_tries,int)
        type_check('max_flips',max_flips,int)
        value_check(
            'context_constructor', context_constructor,
            is_callable = callable,
            arity_2 = has_arity(2)
        )

    #initialize measurement object
    measurement = measurement_constructor(formula, formula.num_vars // 2)

    t = 0
    while t < max_tries:
        if debug:
            print('*',end='',flush=True)
            t_begin = time.time()

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
        if __debug__:
            instance_check('context',context,Context)

        f = 0
        while f < max_flips:
            # check, if the current assignment is a solution
            if context.is_sat():
                if debug:
                    t_end = time.time()
                    t_diff = t_end-t_begin
                    print('Avg time per flip: {} seconds'.format(t_diff/(f+t*max_flips)))
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

    if debug:
        t_end = time.time()
        t_diff = t_end-t_begin
        print('Avg time per flip: {} seconds'.format(t_diff/(max_tries*max_flips)))
    
    return None, measurement
