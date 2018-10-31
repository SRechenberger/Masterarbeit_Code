import os
import random
import sqlite3
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

create_experiment = """
CREATE TABLE IF NOT EXISTS experiment
    ( id            INTEGER PRIMARY KEY
    , solver        TEXT
    , source_folder TEXT
    , sample_size   INT
    )
"""

save_experiment = """
INSERT INTO experiment
    ( solver
    , source_folder
    , sample_size
    )
VALUES (?,?,?)
"""

create_parameter = """
CREATE TABLE IF NOT EXISTS parameter
    ( id                INTEGER PRIMARY KEY
    , experiment_id     INTEGER
    , name              TEXT
    , val               TEXT
    , type              TEXT
    , FOREIGN KEY(experiment_id) REFERENCES experiment(id)
    )
"""

save_parameters = """
INSERT INTO parameters
    ( experiment_id
    , name
    , val
    , type
    )
VALUES (?,?,?,?)
"""

create_algorithm_run = """
CREATE TABLE IF NOT EXISTS algorithm_run
    ( id                INTEGER PRIMARY KEY
    , experiment_id     INTEGER
    , formula           TEXT
    , sat_assgn         TEXT
    , clauses           INT
    , vars              INT
    , sat               BOOL
    , tms_entropy       REAL
    , FOREIGN KEY(experiment_id) REFERENCES experiment(id)
    )
"""

save_algorithm_run = """
INSERT INTO algorithm_run
    ( experiment_id
    , formula
    , sat_assgn
    , clauses
    , vars
    , sat
    , tms_entropy
    )
VALUES (?,?,?,?,?,?,?)
"""

create_search_run = """
CREATE TABLE IF NOT EXISTS search_run
    ( id                INTEGER PRIMARY KEY
    , run_id            INTEGER
    , flips             INT
    , single_entropy    REAL
    , joint_entropy     REAL
    , start_assgn       TEXT
    , end_assgn         TEXT
    , FOREIGN KEY(run_id) REFERENCES algorithm_rum(id)
    )
"""

save_search_run = """
INSERT INTO search_run
    ( run_id
    , flips
    , single_entropy
    , joint_entropy
    , start_assgn
    , end_assgn
    )
VALUES (?,?,?,?,?,?)
"""

class Experiment:
    def __init__(
            self,
            input_dir,              # directory of input files
            sample_size,            # number of files to draw
            solver,                 # the solver to be used
            max_tries, max_flips,   # generic solver parameters
            measurement_constructor,
            evaluation = identity,  # function to transform Measurement instances
            poolsize = 1,           # number of parallel processes
            database = 'experiments.db',
            **solver_params):       # special parameters of the solver

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
            solver_generic  = dict(
                max_tries = max_tries,
                max_flips = max_flips,
            ),
            meta = (
                measurement_constructor,
            )
        )

        self.evaluate = evaluation
        self.poolsize = poolsize
        self.results = None
        self.database = database

        with sqlite3.connect(self.database) as conn:
            c = conn.cursor()
            c.execute(create_experiment)
            c.execute(create_parameter)
            c.execute(create_algorithm_run)
            c.execute(create_search_run)
            conn.commit()



    def _run_solver(self, formula):
        return solvers[self.setup['solver']](
            *self.setup['solver_specific'].values(),
            formula,
            *self.setup['solver_generic'].values(),
            *self.setup['meta']
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


    def save_results(self):
        pass









