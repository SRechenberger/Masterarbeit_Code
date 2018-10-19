from src.solver.utils import Formula, Assignment
from src.experiment.utils import Measurement
from src.utils import *

class Measurement:
    """ Abstract Measurement Class;
    the generic SLS solver needs the given measurement object
    to be an instance of this class or a subclass.
    """
    def init_run(self, assgn):
        raise Warning('Nothing implemented yet.')

    def count(self, flipped_var):
        raise Warning('Nothing implemented yet.')


class Context:
    """ Abstract Context Class;
    the generic SLS solver needs the given context constructor
    to construct an instance of this class or a subclass.
    """
    def update(self, flipped_var):
        raise Warning('Nothing implemented yet.')


def generic_sls(
        heuristic,
        formula,
        max_tries,
        max_flips,
        measurement,
        context_constructor,
        solution_found = None):
    """ Generic SLS-Solver according to Algorithm 1,
    including measurement facilities.
    """

    if __debug__:
        value_check(
            'heuristic',heuristic,
            is_callable = callable,
            arity_3     = has_arity(3)
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
        value_check(
            'solution_found',solution_found,optional = True,
            is_callable = callable,
            arity_1 = has_arity(1)
        )

    #initialize measurement object
    t = 0
    while t < max_tries:
        # generate random assingnment
        current_assignment = Assignment(
            formula.number_of_variables
        )
        # setup measurement object for a search run
        measurement.init_run(current_assignment)

        # initialize context
        context = context_contructor(formula, current_assignment)
        if __debug__:
            instance_check('context',context,Context)

        f = 0
        while f < max_flips:
            # check, if the current assignment is a solution
            if solution_found:
                # either by checking the context, if possible
                if solution_found(context):
                    return current_assignment, measurement
            else:
                ## or by checking the formula
                if formula.is_satisfied_by(current_assignment):
                    return current_assignment

            # choose variable to flip
            to_flip = heuristic(
                formula,
                current_assignment,
                context
            )

            # update context
            context.update(i)

            # register flip in measurement object
            measurement.count_flip(to_flip)

    # If no solution is found,
    # return None
    return None
