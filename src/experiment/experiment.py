import os
import random
import multiprocessing as mp
import src.solver.gsat as gsat
import src.solver.walksat as walksat
import src.solver.probsat as probsat

from functools import partial
from src.utils import *
from src.experiment.utils import FormulaSupply, Measurement

solvers = dict(
    gsat    = gsat.gsat,
    walksat = walksat.walksat,
    probsat = probsat.probsat
)


class Experiment:
    def __init__(
            self,
            input_dir,              # directory of input files
            sample_size,            # number of files to draw
            solver,                 # the solver to be used
            max_tries, max_flips,   # generic solver parameters
            measurement_constructor,
            *solver_params,         # special parameters of the solver
            evaluation = identity,  # function to transform Measurement instances
            poolsize = 1):          # number of parallel processes

        # some checks in debug mode
        if __debug__:
            # checks for 'input_dir'
            type_check('input_dir',input_dir,str)
            value_check('input_dir',input_dir,
                        is_dir = os.path.isdir)
            # checks for 'sample_size'
            type_check('sample_size',sample_size,int)
            value_check('sample_size',sample_size,
                        strict_pos = strict_positive,
                        enough_files = lambda n:
                            n <= len(list(filter(
                                lambda s: s.endswith('.cnf'),
                                os.listdir(input_dir)))))
            # checks for 'solver'
            type_check('solver',solver,str)
            value_check(
                'solver',
                solver,
                is_solver = lambda x: x in solvers
            )
            # checks for 'max_tries'
            type_check('max_tries',max_tries,int)
            value_check('max_tries',max_tries,strict_pos = strict_positive)
            # checks for 'max_flips'
            type_check('max_flips',max_flips,int)
            value_check('max_flips',max_flips,strict_pos = strict_positive)
            # checks for 'measurement_constructor'
            value_check('measurement_constructor',measurement_constructor,
                        is_callable = callable)
            # checks for 'solver_params'
            pass
            # checks for 'evaluation'
            value_check('evaluation',evaluation,
                        is_callable = callable,
                        arity_1 = has_arity(1))
            # checks for 'poolsize'
            type_check('poolsize',poolsize,int)
            value_check('poolsize',poolsize,strict_pos = strict_positive)

        self.formulae = FormulaSupply(
            random.sample(
                list(
                    map(
                        partial(os.path.join,input_dir),
                        filter(
                            lambda s: s.endswith('.cnf'),
                            os.listdir(input_dir),
                        )
                    )
                ),
                sample_size
            ),
            buffsize = poolsize * 10
        )


        self.setup = dict(
            solver = solver,
            solver_specific = solver_params,
            solver_generic  = (
                max_tries,
                max_flips,
                measurement_constructor
            )
        )

        self.evaluate = evaluation
        self.poolsize = poolsize
        self.results = None


    def _run_solver(self, formula):
        return solvers[self.setup['solver']](
            *self.setup['solver_specific'],
            formula,
            *self.setup['solver_generic']
        )


    def run_experiment(self):
        if self.results:
            raise RuntimeError('Experiment already performed')

        self.run = True
        with mp.Pool(processes = self.poolsize) as pool:
            results = pool.map(self._run_solver,self.formulae)

        self.results = list(
            map(
                lambda result: (result[0], self.evaluate(result[1])),
                results
            )
        )
        return self.results


    def __hash__(self):
        return hash(id(self)) % pow(2,32)


    def save_results(self, filename = None, directory = '.'):
        if not filename:
            filename = 'experiment-{:08x}.db'.format(hash(self))

        filepath = os.path.join(directory, filename)
        # TODO









