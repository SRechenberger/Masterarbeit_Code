""" Module defining an random experiment """

import os
import random
import sqlite3
import math
import multiprocessing as mp
import numpy as np
from functools import partial
from bloom_filter import BloomFilter
from scipy.special import binom

from src.solver.gsat import gsat, GSATContext, gsat_distribution
from src.solver.walksat import walksat, DefensiveContext, walksat_distribution
from src.solver.probsat import probsat, probsat_distribution

from src.experiment.utils import FormulaSupply, arr_entropy


CREATE_EXPERIMENT = """
CREATE TABLE IF NOT EXISTS experiment
    ( id            INTEGER PRIMARY KEY
    , solver        TEXT NOT NULL
    , source_folder TEXT NOT NULL
    , sample_size   INT NOT NULL
    , static        BOOL NOT NULL
    )
"""

SAVE_EXPERIMENT = """
INSERT INTO experiment
    ( solver
    , source_folder
    , sample_size
    , static
    )
VALUES (?,?,?,?)
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

CREATE_MEASUREMENT_SERIES = """
CREATE TABLE IF NOT EXISTS measurement_series
    ( id            INTEGER PRIMARY KEY
    , experiment_id INTEGER NOT NULL
    , formula_file  TEXT NOT NULL
    , FOREIGN KEY(experiment_id) REFERENCES experiment(id)
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
INSERT INTO improvement_probability
    ( series_id
    , hamming_dist
    , prob
    )
VALUES (?,?,?)
"""

CREATE_STATE_ENTROPY = """
CREATE TABLE IF NOT EXISTS state_entropy
    ( id            INTEGER PRIMARY KEY
    , series_id     INTEGER NOT NULL
    , hamming_dist  INTEGER NOT NULL
    , entropy_avg   REAL
    , entropy_min   REAL
    , entropy_max   REAL
    , FOREIGN KEY(series_id) REFERENCES measurement_series(id)
    )
"""

SAVE_STATE_ENTROPY = """
INSERT INTO state_entropy
    ( series_id
    , hamming_dist
    , entropy_avg
    , entropy_min
    , entropy_max
    )
VALUES (?,?,?,?,?)
"""

SOLVERS = dict(
  gsat=gsat,
  walksat=walksat,
  probsat=probsat,
)

DISTRS = dict(
  gsat=lambda f: lambda: gsat_distribution,
  walksat=lambda f: walksat_distribution,
  probsat=lambda f: partial(probsat_distribution, f.max_occs),
)

CONTEXTS = dict(
  gsat=GSATContext,
  walksat=DefensiveContext,
  probsat=DefensiveContext,
)  


class AbstractExperiment:


    def __init__(
            self,
            input_dir,
            sample_size,
            solver,
            solver_params,
            is_static,
            *init_database,
            poolsize=1,
            database='experiments.db'):
            

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
            "solver = {} not in {}".format(solver, solvers.keys())
        assert isinstance(solver_params, dict),\
            "solver_params = {} :: {} is no dict".format(solver_params, type(solver_params))
        assert isinstance(poolsize, int),\
            "poolsize = {} :: {} is no int".format(poolsize, type(poolsize))
        assert poolsize > 0,\
            "poolsize = {} <= 0".format(poolsize)
        assert isinstance(database, str),\
            "database = {} :: {} is no str"
        assert all(isinstance(query,str) for query in init_database),\
            "init_database = {} is not a list of str"

        # get solver functions
        self.solver = solver
        self.solver_params = solver_params
        # load formulae
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

        # save poolsize
        self.poolsize = poolsize
        # save database file
        self.database = database
        # no results yet
        self.results = None
        with sqlite3.connect(self.database, timeout=60) as conn:
            # init database, if not already done
            c = conn.cursor()
            c.execute(CREATE_EXPERIMENT)
            c.execute(CREATE_PARAMETER)
            for statement in init_database:
                c.execute(statement)

            c.execute(
                SAVE_EXPERIMENT,
                (
                    solver,
                    input_dir,
                    sample_size,
                    is_static
                )
            )
            self.experiment_id = c.lastrowid

            for k, v in dict(**self.solver_params).items():
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


    def __hash__(self):
        return hash(id(self)) % pow(2, 32)


    def __call__(self):
        """ Runs the prepared experiment """
        if self.results:
            raise RuntimeError('Experiment already performed')
      
        rand_gens = [
          random.Random()
          for _ in range(0,len(self.formulae))
        ]  

        arg_iter = iter(
          (path, formula, rg) 
          for (path, formula), rg in zip(self.formulae, rand_gens)
        )


        if self.poolsize > 1:
            with mp.Pool(processes=self.poolsize) as pool:
                self.results = pool.map(self._run_experiment, arg_iter)
        else:
            self.results = list(map(self._run_experiment, arg_iter))

        return self.results


    def save_result(self, execute, result):
        raise RuntimeError("Abstract Class!")


    def save_results(self):
        """ Saves the results of the experiment """
        assert self.results, "experiment not run"
        with sqlite3.connect(self.database, timeout=60) as conn:
            c = conn.cursor()
            def execute(query, *args):
                c.execute(
                    query,
                    ( *args, )
                )
                return c.lastrowid
            for result in self.results:
                self.save_result(execute, result)
            conn.commit()


class DynamicExperiment(AbstractExperiment):
    """ Random experiment on a set of input formulae """
    def __init__(
            self,
            input_dir,              # directory of input files
            sample_size,            # number of files to draw
            solver,                 # the solver to be used
            solver_params,          # special parameters of the solver
            max_tries, max_flips,   # generic solver parameters
            measurement_constructor,
            poolsize=1,             # number of parallel processes
            database='experiments.db',
            hamming_dist=0):        # start hamming distance

        super(DynamicExperiment, self).__init__(
            input_dir,
            sample_size,
            solver,
            dict(
                max_tries=max_tries,
                max_flips=max_flips,
                **solver_params,
            ),
            False,
            CREATE_ALGORITHM_RUN,
            CREATE_SEARCH_RUN,
            CREATE_ENTROPY_DATA,
            poolsize=poolsize,
            database=database,
        )
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

        self.meta = dict(
            measurement_constructor = measurement_constructor,
            hamming_dist = hamming_dist,
        )


    def _run_experiment(self, args):
        fp, formula, rand_gen = args
        assgn, measurement = SOLVERS[self.solver](
            formula,
            **self.solver_params,
            **self.meta,
            rand_gen=rand_gen
        )

        return dict(
            formula_file=fp,
            sat_assgn=formula.satisfying_assignment,
            num_clauses=formula.num_clauses,
            num_vars=formula.num_vars,
            sat=True if assgn else False,
            runs=measurement.run_measurements,
        )


    def save_result(self, execute, result):
        run_id = execute(
            SAVE_ALGORITHM_RUN,
            self.experiment_id,
            result['formula_file'],
            str(result['sat_assgn']),
            result['num_clauses'],
            result['num_vars'],
            result['sat'],
        )
        for run in result['runs']:
            single_entropy_id = DynamicExperiment.__save_entropy_data(execute, run['single_entropy'])
            joint_entropy_id = DynamicExperiment.__save_entropy_data(execute, run['joint_entropy'])
            mutual_information_id = DynamicExperiment.__save_entropy_data(execute, run['mutual_information'])

            execute(
                SAVE_SEARCH_RUN,
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


    def __save_entropy_data(execute, data):
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

        return execute(
            SAVE_ENTROPY_DATA,
            data['minimum'],
            data['minimum_at'],
            data['maximum'],
            data['maximum_at'],
            data['accum']/data['count']
        )


class StaticExperiment(AbstractExperiment):

    def __init__(
            self,
            input_dir,              # directory of input files
            sample_size,            # number of files to draw
            solver,                 # the solver to be used
            solver_params,          # solver specific parameters
            poolsize=1,             # number of parallel processes
            database='experiments.db'):

        super(StaticExperiment,self).__init__(
            input_dir,
            sample_size,
            solver,
            solver_params,
            True,
            CREATE_MEASUREMENT_SERIES,
            CREATE_IMPROVEMENT_PROB,
            CREATE_STATE_ENTROPY,
            poolsize=poolsize,
            database=database,
        )


    def save_result(self, execute, result):
        for result in self.results:
            run_id = execute(
                SAVE_MEASUREMENT_SERIES,
                self.experiment_id,
                result['formula_file'],
            )
            for series in result['improvement_prob']:
                execute(
                    SAVE_IMPROVEMENT_PROB,
                    run_id,
                    series['hamming_dist'],
                    series['prob'],
                )

            for series in result['avg_state_entropy']:
                execute(
                    SAVE_STATE_ENTROPY,
                    run_id,
                    series['hamming_dist'],
                    series['entropy_avg'],
                    series['entropy_min'],
                    series['entropy_max'],
                )


    def _run_experiment(self, args):
        fp, formula, rand_gen = args
        # calculate the total number of measured states
        n = formula.num_vars
        # get the satisfying assignment
        sat_assgn = formula.satisfying_assignment
        # calculate the assignment with maximum hamming distance to the satisfying one
        furthest_assgn = sat_assgn.negation()
        # init distribution function
        distr_f = DISTRS[self.solver](formula)(**self.solver_params)

        # calculate the total number of measured states
        total_num_states = sum(
            map(
                lambda i: int(.5 * math.log(i)+1) * (n - 2*i + 1),
                range(1, n // 2 + 1)
            )
        )
        # initialize the bloom filter
        measured_states = BloomFilter(max_elements = total_num_states, error_rate = 0.2)

        # initialize three array:
        #   state_count[i] counts the number of states at distance i
        #   state_entropy[i] accumulates the state_entropy at distance i
        #   state_entropy_min[i] holds the minimum state entropy found at distance i
        #   state_entropy_max[i] holds the maximum state entropy found at distance i
        #   increment_prob[i] accumuluates the probability of incrementation at distance i
        # indices 0 and n are known
        state_count = np.zeros(n+1)
        # one state at each end
        state_count[0], state_count[n] = 1, 1
        state_entropy = np.zeros(n+1)
        state_entropy_min = np.ones(n+1) * math.log(n,2)
        state_entropy_max = np.zeros(n+1)
        state_entropy_min[0], state_entropy_max[0] = 0, 0
        state_entropy_min[n], state_entropy_max[n] = 0, 0
        # entropy at the ends is 0, because there are no uncertainties
        increment_prob = np.zeros(n+1)
        decrement_prob = np.zeros(n+1)
        # at the negated assignment every flip is good; on the other end, every flip is bad
        increment_prob[0] = 1
        decrement_prob[n] = 1

        # for each hamming distance beginning with 1
        for distance in range(1,n // 2 + 1):
            # calculate number of paths to run from this distance
            num_paths = int(math.log(distance) + 1)
            # for each path
            for i in range(0,num_paths):
                # copy the left end assignment
                current_assgn = furthest_assgn.copy()
                # get a path to a random node 'distance' steps away
                differ, _ = current_assgn.hamming_sets(sat_assgn)
                # walk to the start node of the path
                for step in rand_gen.sample(differ, distance):
                    current_assgn.flip(step)

                # init context
                ctx = CONTEXTS[self.solver](formula, current_assgn)
                # variables for measured path
                differ, same = current_assgn.hamming_sets(sat_assgn)
                path = rand_gen.sample(differ, n - distance)
                path_set = set(differ)
                check_set = set(same)

                hamming_dist = distance
                for step in path:
                    # calculate distribution
                    distr = distr_f(ctx)
                    # current hamming distance
                    assgn_str = str(current_assgn)
                    # if this state was not already measured
                    if assgn_str not in measured_states:
                        # increment counter for this hamming distance
                        state_count[hamming_dist] += 1
                        # calculate incrementation probability
                        prob = 0
                        for i in path_set:
                            prob += distr[i]

                        co_prob = 0
                        for i in check_set:
                            co_prob += distr[i]

                        increment_prob[hamming_dist] += prob
                        decrement_prob[hamming_dist] += co_prob


                        # calculate state entropy
                        h = arr_entropy(distr)
                        state_entropy[hamming_dist] += h
                        state_entropy_max[hamming_dist] = max(state_entropy_max[hamming_dist],h)
                        state_entropy_min[hamming_dist] = min(state_entropy_min[hamming_dist],h)

                        # add this assignment to the set of measured states
                        measured_states.add(assgn_str)

                    # remove walked step form differ
                    path_set.remove(step)
                    check_set.add(step)
                    # make the step
                    hamming_dist -= 1
                    ctx.update(step)

        # postprocessing
        divide = np.vectorize(lambda v, c: v / c if c != 0 else 0)
        state_entropy = divide(state_entropy, state_count)
        calc_prob = np.vectorize(lambda inc, dec: inc/(inc+dec))
        increment_prob = calc_prob(increment_prob, state_count)

        return dict(
            formula_file=fp,
            improvement_prob=[
                dict(hamming_dist=d, prob=p)
                for d,p in enumerate(increment_prob)
            ],
            avg_state_entropy=[
                dict(hamming_dist=d, entropy_avg=h, entropy_max=h_max, entropy_min=h_min)
                for d,(h,h_min,h_max) in enumerate(
                    zip(state_entropy,state_entropy_min,state_entropy_max)
                )
            ],
        )
