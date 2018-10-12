from src.solver.utils import Formula, Assignment
from src.experiment.utils import Measurement

def generic_sls(
        heuristic,
        formula,
        max_tries,
        max_flips
        solution_found = None,
        init_context = lambda formula assignment: None,
        update_context = lambda state variable: None,
    ):
    """ Generic SLS-Solver according to Algorithm 1,
    including measurement facilities.
    """

    #initialize measurement object
    measurement = Measurement(
        formula.satisfying_assignment
    )

    t = 0
    while t < max_tries:
        # generate random assingnment
        current_assignment = Assignment(
            formula.number_of_variables
        )
        # setup measurement object for a search run
        measurement.init_run(current_assignment)

        # initialize context
        context = init_context(formula, current_assignment)

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
                    return current_assignment, measurement

            # choose variable to flip
            to_flip = heuristic(
                formula,
                current_assignment,
                context
            )

            # flip variable
            current_assignment = current_assignment.flip(to_flip)

            # update context
            context = update_context(s, i)

            # register flip in measurement object
            measurement.count_flip(to_flip)

    # If no solution is found,
    # return None and the measurement object
    return None, measurement
