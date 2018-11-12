""" Module defining an random experiment """

import os
import random
import sqlite3
import multiprocessing as mp
from functools import partial

from src.solver.gsat import gsat
from src.solver.walksat import walksat
from src.solver.probsat import probsat

from src.experiment.utils import FormulaSupply

SOLVERS = dict(
    gsat=gsat,
    walksat=walksat,
    probsat=probsat
)

CREATE_EXPERIMENT = """
CREATE TABLE IF NOT EXISTS experiment
    ( id            INTEGER PRIMARY KEY
    , solver        TEXT NOT NULL
    , source_folder TEXT NOT NULL
    , sample_size   INT NOT NULL
    )
"""

SAVE_EXPERIMENT = """
INSERT INTO experiment
    ( solver
    , source_folder
    , sample_size
    )
VALUES (?,?,?)
"""

CREATE_PARAMETER = """
CREATE TABLE IF NOT EXISTS parameter
    ( id                INTEGER PRIMARY KEY
    , experiment_id     INTEGER NOT NULL
    , name              TEXT NOT NULL
    , val               TEXT NOT NULL
    , type              TEXT NOT NULL
    , FOREIGN KEY(experiment_id) REFERENCES experiment(id)
    )
"""

SAVE_PARAMETER = """
INSERT INTO parameter
    ( experiment_id
    , name
    , val
    , type
    )
VALUES (?,?,?,?)
"""

CREATE_ALGORITHM_RUN = """
CREATE TABLE IF NOT EXISTS algorithm_run
    ( id                INTEGER PRIMARY KEY
    , experiment_id     INTEGER NOT NULL
    , formula_file      TEXT NOT NULL
    , sat_assgn         TEXT NOT NULL
    , clauses           INT NOT NULL
    , vars              INT NOT NULL
    , sat               BOOL NOT NULL
    , tms_entropy       REAL NOT NULL
    , FOREIGN KEY(experiment_id) REFERENCES experiment(id)
    )
"""

SAVE_ALGORITHM_RUN = """
INSERT INTO algorithm_run
    ( experiment_id
    , formula_file
    , sat_assgn
    , clauses
    , vars
    , sat
    , tms_entropy
    )
VALUES (?,?,?,?,?,?,?)
"""

CREATE_SEARCH_RUN = """
CREATE TABLE IF NOT EXISTS search_run
    ( id                    INTEGER PRIMARY KEY
    , run_id                INTEGER NOT NULL
    , flips                 INT NOT NULL
    , single_entropy        REAL NOT NULL
    , joint_entropy         REAL NOT NULL
    , mutual_information    REAL NOT NULL
    , hamming_dist          INT NOT NULL
    , start_assgn           TEXT NOT NULL
    , end_assgn             TEXT NOT NULL
    , success               BOOL NOT NULL
    , FOREIGN KEY(run_id) REFERENCES algorithm_rum(id)
    )
"""

SAVE_SEARCH_RUN = """
INSERT INTO search_run
    ( run_id
    , flips
    , single_entropy
    , joint_entropy
    , hamming_dist
    , mutual_information
    , start_assgn
    , end_assgn
    , success
    )
VALUES (?,?,?,?,?,?,?,?,?)
"""

class Experiment:
    """ Random experiment on a set of input formulae """
    def __init__(
            self,
            input_dir,              # directory of input files
            sample_size,            # number of files to draw
            solver,                 # the solver to be used
            max_tries, max_flips,   # generic solver parameters
            measurement_constructor,
            poolsize=1,             # number of parallel processes
            database='experiments.db',
            **solver_params):       # special parameters of the solver

        # some checks in debug mode
        assert isinstance(input_dir, str),\
            "input_dir = {} :: {} is no str".format(input_dir, type(input_dir))
        assert os.path.isdir(input_dir),\
            "input_dir = {} is no directory".format(input_dir)
        assert isinstance(sample_size, int),\
            "sample_size = {} :: {} is no int".format(sample_size, type(sample_size))
        assert sample_size > 0,\
            "sample_size = {} <= 0".format(sample_size)
        assert isinstance(solver, str),\
            "solver = {} :: {} is no str".format(solver, type(solver))
        assert solver in SOLVERS,\
            "solver = {} not in {}".format(solver, SOLVERS)
        assert isinstance(max_tries, int),\
            "max_tries = {} :: {} is no int".format(max_tries, type(max_tries))
        assert max_tries > 0,\
            "max_tries = {} <= 0".format(max_tries)
        assert isinstance(max_flips, int),\
            "max_flips = {} :: {} is no int".format(max_flips, type(max_flips))
        assert max_flips > 0,\
            "max_flips = {} <= 0".format(max_flips)
        assert callable(measurement_constructor),\
            "measurement_constructor = {} is not callable".format(measurement_constructor)
        assert isinstance(poolsize, int),\
            "poolsize = {} :: {} is no int".format(poolsize, type(poolsize))
        assert poolsize > 0,\
            "poolsize = {} <= 0".format(poolsize)


        self.formulae = FormulaSupply(
            random.sample(
                list(
                    map(
                        partial(os.path.join, input_dir),
                        filter(
                            lambda s: s.endswith('.cnf'),
                            os.listdir(input_dir),
                        )
                    )
                ),
                sample_size
            ),
            buffsize=poolsize * 10
        )

        solver_generic_params = dict(
            max_tries=max_tries,
            max_flips=max_flips,
        )

        self.setup = dict(
            solver=solver,
            solver_specific=solver_params,
            solver_generic=solver_generic_params,
            meta=(measurement_constructor,)
        )

        self.poolsize = poolsize
        self.results = None
        self.database = database
        self.run = False

        with sqlite3.connect(self.database, timeout=60) as conn:
            # init database, if not already done
            c = conn.cursor()
            c.execute(CREATE_EXPERIMENT)
            c.execute(CREATE_PARAMETER)
            c.execute(CREATE_ALGORITHM_RUN)
            c.execute(CREATE_SEARCH_RUN)
            conn.commit()

            # save this experiment
            c.execute(
                SAVE_EXPERIMENT,
                (
                    solver,
                    input_dir,
                    sample_size
                )
            )
            self.experiment_id = c.lastrowid

            for k, v in dict(**solver_generic_params, **solver_params).items():
                c.execute(
                    SAVE_PARAMETER,
                    (
                        self.experiment_id,
                        k,
                        str(v),
                        type(v).__name__,
                    )
                )
            conn.commit()


    def _run_solver(self, fp_and_formula):
        fp, formula = fp_and_formula
        assgn, measurement = SOLVERS[self.setup['solver']](
            formula,
            *self.setup['meta'],
            **self.setup['solver_generic'],
            **self.setup['solver_specific'],
        )

        return dict(
            formula_file=fp,
            sat_assgn=formula.satisfying_assignment,
            num_clauses=formula.num_clauses,
            num_vars=formula.num_vars,
            sat=True if assgn else False,
            tms_entropy=measurement.get_tms_entropy(),
            runs=measurement.run_measurements,
        )


    def run_experiment(self):
        """ Runs the prepared experiment """
        if self.results:
            raise RuntimeError('Experiment already performed')

        self.run = True
        with mp.Pool(processes=self.poolsize) as pool:
            self.results = pool.map(self._run_solver, self.formulae)

        return self.results


    def __hash__(self):
        return hash(id(self)) % pow(2, 32)


    def save_results(self):
        """ Saves the results of the experiment """
        assert self.run, "experiment not run"
        with sqlite3.connect(self.database, timeout=60) as conn:
            c = conn.cursor()
            for result in self.results:
                c.execute(
                    SAVE_ALGORITHM_RUN,
                    (
                        self.experiment_id,
                        result['formula_file'],
                        str(result['sat_assgn']),
                        result['num_clauses'],
                        result['num_vars'],
                        result['sat'],
                        result['tms_entropy'],
                    )
                )
                run_id = c.lastrowid
                for run in result['runs']:
                    c.execute(
                        SAVE_SEARCH_RUN,
                        (
                            run_id,
                            run['flips'],
                            run['single_entropy'],
                            run['joint_entropy'],
                            run['mututal_information'],
                            run['hamming_dist'],
                            run['start_assgn'],
                            run['final_assgn'],
                            run['success'],
                        )
                    )
                conn.commit()
