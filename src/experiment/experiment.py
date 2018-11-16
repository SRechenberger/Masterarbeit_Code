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
    )
VALUES (?,?,?,?,?,?)
"""

CREATE_SEARCH_RUN = """
CREATE TABLE IF NOT EXISTS search_run
    ( id                    INTEGER PRIMARY KEY
    , run_id                INTEGER NOT NULL
    , flips                 INT NOT NULL
    , single_entropy        INTEGER
    , joint_entropy         INTEGER
    , mutual_information    INTEGER
    , hamming_dist          INT NOT NULL
    , start_assgn           TEXT NOT NULL
    , end_assgn             TEXT NOT NULL
    , success               BOOL NOT NULL
    , FOREIGN KEY(run_id) REFERENCES algorithm_rum(id)
    , FOREIGN KEY(single_entropy) REFERENCES entropy_data(id)
    , FOREIGN KEY(joint_entropy) REFERENCES entropy_data(id)
    , FOREIGN KEY(mutual_information) REFERENCES entropy_data(id)
    )
"""

SAVE_SEARCH_RUN = """
INSERT INTO search_run
    ( run_id
    , flips
    , single_entropy
    , joint_entropy
    , mutual_information
    , hamming_dist
    , start_assgn
    , end_assgn
    , success
    )
VALUES (?,?,?,?,?,?,?,?,?)
"""

CREATE_ENTROPY_DATA = """
CREATE TABLE IF NOT EXISTS entropy_data
    ( id            INTEGER PRIMARY KEY
    , minimum       REAL
    , minimum_at    INTEGER
    , maximum       REAL
    , maximum_at    INTEGER
    , average       REAL
    )
"""

SAVE_ENTROPY_DATA = """
INSERT INTO entropy_data
    ( minimum
    , minimum_at
    , maximum
    , maximum_at
    , average
    )
VALUES (?,?,?,?,?)
"""


CREATE_STATIC_EXPERIMENT = """
CREATE TABLE IF NOT EXISTS static_experiment
    ( id            INTEGER PRIMARY KEY
    , solver        TEXT NOT NULL
    , source_folder TEXT NOT NULL
    , sample_size   TEXT NOT NULL
    )
"""

SAVE_STATIC_EXPERIMENT = """
INSERT INTO static_experiment
    ( solver
    , source_folder
    , sample_size
    )
VALUES (?,?,?)
"""

CREATE_MEASUREMENT_SERIES = """
CREATE TABLE IF NOT EXISTS measurement_series
    ( id            INTEGER PRIMARY KEY
    , experiment_id INTEGER NOT NULL
    , formula_file  TEXT NOT NULL
    , FOREIGN KEY(experiment_id) REFERENCES static_experiment(id)
    )
"""

SAVE_MEASUREMENT_SERIES = """
INSERT INTO measurement_series
    ( experiment_id
    , formula_file
    )
VALUES (?,?)
"""

CREATE_IMPROVEMENT_PROB = """
CREATE TABLE IF NOT EXISTS improvement_probability
    ( id            INTEGER PRIMARY KEY
    , series_id     INTEGER NOT NULL
    , hamming_dist  INTEGER NOT NULL
    , prob          REAL
    , FOREIGN KEY(series_id) REFERENCES measurement_series(id)
    )
"""

SAVE_IMPROVEMENT_PROB = """
INSERT INTO TABLE improvement_probability
    ( series_id
    , hamming_dist
    , prob
    )
VALUE (?,?,?)
"""

CREATE_AVG_STATE_ENTROPY = """
CREATE TABLE IF NOT EXISTS avg_state_entropy
    ( id            INTEGER PRIMARY KEY
    , series_id     INTEGER NOT NULL
    , hamming_dist  INTEGER NOT NULL
    , entropy       REAL
    , FOREIGN KEY(series_id) REFERENCES measurement_series(id)
    )
"""

SAVE_AVG_STATE_ENTROPY = """
INSERT INTO TABLE improvement_probability
    ( series_id
    , hamming_dist
    , entropy
    )
VALUE (?,?,?)
"""

def save_entropy_data(cursor, data):
    assert isinstance(data,dict),\
        "data = {} :: {} is no dict".format(data, type(data))
    assert 'minimum' in data,\
        "minimum not in data = {}".format(data)
    assert 'minimum_at' in data,\
        "mimimum_at not in data = {}".format(data)
    assert 'maximum' in data,\
        "maximum not in data = {}".format(data)
    assert 'maximum_at' in data,\
        "maximum_at not in data = {}".format(data)
    assert 'accum' in data,\
        "accum not in data = {}".format(data)
    assert 'count' in data,\
        "count not in data = {}".format(data)


    if data['accum'] <= 0:
        return None

    cursor.execute(
        SAVE_ENTROPY_DATA,
        (
            data['minimum'],
            data['minimum_at'],
            data['maximum'],
            data['maximum_at'],
            data['accum']/data['count']
        )
    )

    return cursor.lastrowid


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
            c.execute(CREATE_ENTROPY_DATA)
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
                    )
                )
                run_id = c.lastrowid
                for run in result['runs']:

                    single_entropy_id = save_entropy_data(c, run['single_entropy'])
                    joint_entropy_id = save_entropy_data(c, run['joint_entropy'])
                    mutual_information_id = save_entropy_data(c, run['mutual_information'])

                    c.execute(
                        SAVE_SEARCH_RUN,
                        (
                            run_id,
                            run['flips'],
                            single_entropy_id,
                            joint_entropy_id,
                            mutual_information_id,
                            run['hamming_dist'],
                            run['start_assgn'],
                            run['final_assgn'],
                            run['success'],
                        )
                    )
                conn.commit()


class StaticExperiment:

    def __init__(
            self,
            input_dir,              # directory of input files
            sample_size,            # number of files to draw
            solver,                 # the solver to be used
            poolsize=1,             # number of parallel processes
            database='experiments.db',
            **solver_params):       # special parameters of the solver

        # TODO assertions
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
        )

        self.poolsize = poolsize
        self.results = None
        self.database = database
        self.run = False

        with sqlite3.connect(self.database, timeout=60) as conn:
            # init database, if not already done
            c = conn.cursor()
            c.execute(CREATE_STATIC_EXPERIMENT)
            c.execute(CREATE_MEASUREMENT_SERIES)
            c.execute(CREATE_IMPROVEMENT_PROB)
            c.execute(CREATE_AVG_STATE_ENTROPY)
            conn.commit()

            # save this experiment
            c.execute(
                SAVE_STATIC_EXPERIMENT,
                (
                    solver,
                    input_dir,
                    sample_size
                )
            )
            self.experiment_id = c.lastrowid

            for k, v in solver_params.items():
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


    def _run_measurement(self, fp_and_formula):
        fp, formula = fp_and_formula
        # TODO
        raise RuntimError("Not Implemented Yet")

        return None


    def run_experiment(self):
        """ Runs the prepared experiment """
        if self.results:
            raise RuntimeError('Experiment already performed')

        self.run = True
        with mp.Pool(processes=self.poolsize) as pool:
            self.results = pool.map(self._run_measurement, self.formulae)

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
                    SAVE_MEASUREMENT_SERIES,
                    (
                        self.experiment_id,
                        result['formula_file'],
                    )
                )
                run_id = c.lastrowid
                for series in result['improvement_prob']:
                    c.execute(
                        SAVE_IMPROVEMENT_PROB,
                        (
                            run_id,
                            series['hamming_dist'],
                            series['prob'],
                        )
                    )

                for series in result['avg_state_entropy']:
                    c.execute(
                        SAVE_AVG_STATE_ENTROPY,
                        (
                            run_id,
                            series['hamming_dist'],
                            series['entropy'],
                        )
                    )
                conn.commit()

