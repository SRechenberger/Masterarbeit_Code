from src.solver.utils import Formula, Assignment
from src.experiment.utils import Measurement
from src.utils import *

import time

debug = True

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
        measurement):
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
        instance_check('measurement',measurement,Measurement)
        value_check(
            'context_constructor', context_constructor,
            is_callable = callable,
            arity_2 = has_arity(2)
        )

    #initialize measurement object
    t = 0
    while t < max_tries:
        if debug:
            print('*',end='',flush=True)
            t_begin = time.time()
        # generate random assingnment
        current_assignment = Assignment.generate_random_assignment(
            formula.num_vars
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
                return current_assignment

            # choose variable to flip
            to_flip = heuristic(context)

            # update context
            # also modifies 'current_assignment'
            context.update(to_flip)

            # register flip in measurement object
            measurement.count(to_flip)

    # If no solution is found,
    # return None
    
    if debug:
        t_end = time.time()
        t_diff = t_end-t_begin
        print('Avg time per flip: {} seconds'.format(t_diff/(max_tries*max_flips)))
    return None
