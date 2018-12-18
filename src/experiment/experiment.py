""" Module defining an random experiment """

import os
import random
import sqlite3
import math
import multiprocessing as mp
from functools import partial

from src.formula import Formula

from src.solver.gsat import gsat, GSATContext, gsat_distribution
from src.solver.walksat import walksat, DefensiveContext, walksat_distribution
from src.solver.probsat import probsat, probsat_distribution

from src.experiment.utils import FormulaSupply, arr_entropy
from src.experiment.measurement import RuntimeMeasurement


CREATE_EXPERIMENT = """
CREATE TABLE IF NOT EXISTS experiment
    ( experiment_id INTEGER PRIMARY KEY
    , repetition_of INTEGER
    , solver        TEXT NOT NULL
    , noise_param   REAL NOT NULL
    , max_tries     INTEGER NOT NULL
    , max_flips     INTEGER NOT NULL
    , sample_size   INT NOT NULL
    , static        BOOL NOT NULL
    , FOREIGN KEY(repetition_of) REFERENCES experiment(experiment_id)
    )
"""

SAVE_EXPERIMENT = """
INSERT INTO experiment
    ( repetition_of
    , solver
    , noise_param
    , max_tries
    , max_flips
    , sample_size
    , static
    )
VALUES (?,?,?,?,?,?,?)
"""

CREATE_FORMULA = """
CREATE TABLE IF NOT EXISTS formula
    ( formula_id    INTEGER PRIMARY KEY
    , formula_file  TEXT NOT NULL
    , num_vars      INTEGER NOT NULL
    , num_clauses   INTEGER NOT NULL
    , sat_assgn     TEXT NOT NULL
    )
"""

SAVE_FORMULA = """
INSERT INTO formula
    ( formula_file 
    , num_vars
    , num_clauses
    , sat_assgn
    )
VALUES (?, ?, ?, ?)
"""

CREATE_ALGORITHM_RUN = """
CREATE TABLE IF NOT EXISTS algorithm_run
    ( run_id            INTEGER PRIMARY KEY
    , experiment_id     INTEGER NOT NULL
    , formula_id        INTEGER NOT NULL
    , sat               BOOL NOT NULL
    , total_runtime     INTEGER NOT NULL
    , FOREIGN KEY(experiment_id) REFERENCES experiment(experiment_id)
    , FOREIGN KEY(formula_id) REFERENCES formula(formula_id)
    )
"""

SAVE_ALGORITHM_RUN = """
INSERT INTO algorithm_run
    ( experiment_id
    , formula_id
    , sat
    , total_runtime
    )
VALUES (?,?,?,?)
"""

CREATE_SEARCH_RUN = """
CREATE TABLE IF NOT EXISTS search_run
    ( search_id             INTEGER PRIMARY KEY
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
    ( data_id       INTEGER PRIMARY KEY
    , latest        REAL
    , latest_at     INTEGER
    , minimum       REAL
    , minimum_at    INTEGER
    , maximum       REAL
    , maximum_at    INTEGER
    , average       REAL
    )
"""

SAVE_ENTROPY_DATA = """
INSERT INTO entropy_data
    ( latest
    , latest_at
    , minimum
    , minimum_at
    , maximum
    , maximum_at
    , average
    )
VALUES (?,?,?,?,?,?,?)
"""

CREATE_MEASUREMENT_SERIES = """
CREATE TABLE IF NOT EXISTS measurement_series
    ( series_id     INTEGER PRIMARY KEY
    , experiment_id INTEGER NOT NULL
    , formula_id    INTEGER NOT NULL
    , measured_states INTEGER NOT NULL
    , max_measured_states INTEGER NOT NULL
    , FOREIGN KEY(experiment_id) REFERENCES experiment(experiment_id)
    , FOREIGN KEY(formula_id) REFERENCES formula(formula_id)
    )
"""

SAVE_MEASUREMENT_SERIES = """
INSERT INTO measurement_series
    ( experiment_id
    , formula_id
    , measured_states
    , max_measured_states
    )
VALUES (?,?,?,?)
"""

CREATE_IMPROVEMENT_PROB = """
CREATE TABLE IF NOT EXISTS improvement_probability
    ( prob_id       INTEGER PRIMARY KEY
    , series_id     INTEGER NOT NULL
    , hamming_dist  INTEGER NOT NULL
    , prob          REAL
    , FOREIGN KEY(series_id) REFERENCES measurement_series(series_id)
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

CREATE_UNSAT_CLAUSES = """
CREATE TABLE IF NOT EXISTS unsat_clauses
    ( unsat_clauses_id  INTEGER PRIMARY KEY
    , series_id         INTEGER NOT NULL
    , hamming_dist      INTEGER NOT NULL
    , unsat_clauses     REAL
    , FOREIGN KEY(series_id) REFERENCES measurement_series(series_id)
    )
"""

SAVE_UNSAT_CLAUSES = """
INSERT INTO unsat_clauses
    ( series_id
    , hamming_dist
    , unsat_clauses
    )
VALUES (?,?,?)
"""

CREATE_STATE_ENTROPY = """
CREATE TABLE IF NOT EXISTS state_entropy
    ( state_entropy_id INTEGER PRIMARY KEY
    , series_id     INTEGER NOT NULL
    , hamming_dist  INTEGER NOT NULL
    , entropy_avg   REAL
    , entropy_min   REAL
    , entropy_max   REAL
    , FOREIGN KEY(series_id) REFERENCES measurement_series(series_id)
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
  gsat=gsat_distribution,
  walksat=walksat_distribution,
  probsat=probsat_distribution,
)

CONTEXTS = dict(
  gsat=GSATContext,
  walksat=DefensiveContext,
  probsat=DefensiveContext,
)


class AbstractExperiment:

    def __init__(
            self,
            input_files,
            solver,
            solver_params,
            is_static,
            repetition_of,
            *init_database,
            poolsize=1,
            database='experiments.db'):

        assert all([os.path.isfile(input_file) for input_file in input_files]),\
            "input_files = {} is no List[str]".format(input_files)
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
        self.repetition_of = repetition_of
        # load formulae
        #self.formulae = FormulaSupply(
        #    input_files,
        #    buffsize=min(len(input_files), poolsize * 10)
        #)



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
            c.execute(CREATE_FORMULA)
            for statement in init_database:
                c.execute(statement)

            self.formulae = []
            for file in input_files:
                with open(file, 'r') as f:
                    formula = Formula(dimacs=f.read())
                res = c.execute(
                    'SELECT formula_id FROM formula WHERE formula_file like ?',
                    (file,)
                )
                res = list(res)
                if len(res) == 0:
                    c.execute(
                        SAVE_FORMULA,
                        (
                            file,
                            formula.num_vars,
                            formula.num_clauses,
                            str(formula.satisfying_assignment)
                        )
                    )
                    formula_id = c.lastrowid
                elif len(res) > 0:
                    formula_id, = res[0]

                self.formulae.append((formula_id, formula))

            c.execute(
                SAVE_EXPERIMENT,
                (
                    self.repetition_of,
                    solver,
                    solver_params['noise_param'],
                    solver_params['max_tries'],
                    solver_params['max_flips'],
                    len(input_files),
                    is_static
                )
            )

            self.experiment_id = c.lastrowid
            conn.commit()


    def __hash__(self):
        return hash(id(self)) % pow(2, 32)


    def __call__(self):
        """ Runs the prepared experiment """
        if self.results:
            raise RuntimeError('Experiment already performed')

        rand_gens = iter(
          random.Random()
          for _ in range(0,len(self.formulae))
        )

        arg_iter = iter(
          (f_id, formula, rg)
          for (f_id, formula), rg in zip(self.formulae, rand_gens)
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
            input_files,            # list of input files
            solver,                 # the solver to be used
            solver_params,          # parameters of the solver
            measurement_constructor,
            poolsize=1,             # number of parallel processes
            database='experiments.db',
            hamming_dist=0,         # start hamming distance
            repetition_of=None):

        super(DynamicExperiment, self).__init__(
            input_files,
            solver,
            solver_params,
            False,
            repetition_of,
            CREATE_ALGORITHM_RUN,
            CREATE_SEARCH_RUN,
            CREATE_ENTROPY_DATA,
            poolsize=poolsize,
            database=database,
        )
        assert 'max_tries' in solver_params and 'max_flips' in solver_params and 'noise_param' in solver_params,\
            f"max_tries, max_flips or noise_param is not in {solver_params}"
        assert isinstance(solver_params['max_tries'], int),\
            "max_tries = {} :: {} is no int".format(solver_params['max_tries'], type(solver_params['max_tries']))
        assert solver_params['max_tries'] > 0,\
            "max_tries = {} <= 0".format(solver_params['max_tries'])
        assert isinstance(solver_params['max_flips'], int),\
            "max_flips = {} :: {} is no int".format(solver_params['max_flips'], type(solver_params['max_flips']))
        assert solver_params['max_flips'] > 0,\
            "max_flips = {} <= 0".format(solver_params['max_flips'])
        assert callable(measurement_constructor),\
            "measurement_constructor = {} is not callable".format(measurement_constructor)

        self.meta = dict(
            measurement_constructor = measurement_constructor,
            hamming_dist = hamming_dist,
        )


    def _run_experiment(self, args):
        f_id, formula, rand_gen = args
        assgn, measurement = SOLVERS[self.solver](
            formula,
            **self.solver_params,
            **self.meta,
            rand_gen=rand_gen
        )

        return dict(
            formula_id=f_id,
            sat=True if assgn else False,
            runs=measurement.run_measurements,
        )


    def save_result(self, execute, result):
        run_id = execute(
            SAVE_ALGORITHM_RUN,
            self.experiment_id,
            result['formula_id'],
            result['sat'],
            sum(iter(run['flips'] for run in result['runs'])),
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
            data['latest'],
            data['latest_at'],
            data['minimum'],
            data['minimum_at'],
            data['maximum'],
            data['maximum_at'],
            data['accum']/data['count']
        )


class StaticExperiment(AbstractExperiment):

    def __init__(
            self,
            input_files,            # list of input files
            solver,                 # the solver to be used
            solver_params,          # solver specific parameters
            poolsize=1,             # number of parallel processes
            database='experiments.db',
            repetition_of=None):

        super(StaticExperiment,self).__init__(
            input_files,
            solver,
            dict(
                max_tries=0,
                max_flips=0,
                noise_param=solver_params['noise_param'],
            ),
            True,
            repetition_of,
            CREATE_MEASUREMENT_SERIES,
            CREATE_IMPROVEMENT_PROB,
            CREATE_STATE_ENTROPY,
            CREATE_UNSAT_CLAUSES,
            poolsize=poolsize,
            database=database,
        )


    def save_result(self, execute, result):
        series_id = execute(
            SAVE_MEASUREMENT_SERIES,
            self.experiment_id,
            result['formula_id'],
            result['measured_states'],
            result['max_measured_states'],
        )

        for series in result['improvement_prob']:
            execute(
                SAVE_IMPROVEMENT_PROB,
                series_id,
                series['hamming_dist'],
                series['prob'],
            )

        for series in result['avg_state_entropy']:
            execute(
                SAVE_STATE_ENTROPY,
                series_id,
                series['hamming_dist'],
                series['entropy_avg'],
                series['entropy_min'],
                series['entropy_max'],
            )

        for series in result['unsat_clauses']:
            execute(
                SAVE_UNSAT_CLAUSES,
                series_id,
                series['hamming_dist'],
                series['unsat_clauses'],
            )


    def _run_experiment(self, args):
        f_id, formula, rand_gen = args
        # calculate the total number of measured states
        n = formula.num_vars
        # get the satisfying assignment
        sat_assgn = formula.satisfying_assignment
        # calculate the assignment with maximum hamming distance to the satisfying one
        furthest_assgn = sat_assgn.negation()
        # init distribution function
        distr_f = DISTRS[self.solver](self.solver_params['noise_param'])

        path_count = lambda i: max(1, i // 3 * 2)

        # initialize the bloom filter
        measured_states = set()

        # initialize three array:
        #   state_count[i] counts the number of states at distance i
        #   state_entropy[i] accumulates the state_entropy at distance i
        #   state_entropy_min[i] holds the minimum state entropy found at distance i
        #   state_entropy_max[i] holds the maximum state entropy found at distance i
        #   increment_prob[i] accumuluates the probability of incrementation at distance i
        # indices 0 and n are known
        state_count = [0] * (n+1)
        # one state at each end
        state_count[0], state_count[n] = 1, 1
        state_entropy = [0] * (n+1)
        state_entropy_min = [math.log(n,2)] * (n+1)
        state_entropy_max = [0] * (n+1)
        state_entropy_min[0], state_entropy_max[0] = 0, 0
        state_entropy_min[n], state_entropy_max[n] = 0, 0
        # entropy at the ends is 0, because there are no uncertainties
        increment_prob = [0] * (n+1)
        # at the negated assignment every flip is good; on the other end, every flip is bad
        increment_prob[n] = 1

        unsat_clauses = [0] * (n+1)

        # for each hamming distance beginning with 1
        for distance in range(1,n // 2 + 1):
            # calculate number of paths to run from this distance
            num_paths = path_count(distance)
            # for each path
            for i in range(0,num_paths):
                # copy the left end assignment
                current_assgn = furthest_assgn.copy()
                # get a path to a random node 'distance' steps away
                # walk to the start node of the path
                for step in rand_gen.sample(range(1,n+1), distance):
                    current_assgn.flip(step)

                # init context
                ctx = CONTEXTS[self.solver](formula, current_assgn)
                flist = ctx.falselist
                # variables for measured path
                differ, same = current_assgn.hamming_sets(sat_assgn)
                path = rand_gen.sample(differ, n - 2*distance + 1)
                path_set = set(differ)
                check_set = set(same)

                hamming_dist = n - distance
                for step in path:
                    # calculate distribution
                    distr = distr_f(ctx)
                    # current hamming distance
                    assgn_num = current_assgn.number
                    # if this state was not already measured
                    if assgn_num not in measured_states:
                        # increment counter for this hamming distance
                        state_count[hamming_dist] += 1
                        # calculate incrementation probability
                        prob = distr[0] * len(path_set)/n
                        for i in path_set:
                            prob += distr[i]

                        increment_prob[hamming_dist] += prob
                        unsat_clauses[hamming_dist] += len(flist)

                        # calculate state entropy
                        h = arr_entropy(distr, base=n+1)
                        state_entropy[hamming_dist] += h
                        state_entropy_max[hamming_dist] = max(state_entropy_max[hamming_dist],h)
                        state_entropy_min[hamming_dist] = min(state_entropy_min[hamming_dist],h)

                        # add this assignment to the set of measured states
                        measured_states.add(assgn_num)

                    # remove walked step form differ
                    path_set.remove(step)
                    check_set.add(step)
                    # make the step
                    hamming_dist -= 1
                    ctx.update(step)

        # postprocessing
        #for i, (inc, dec) in enumerate(zip(increment_prob, decrement_prob)):
        #    assert inc + dec > 0 ,\
        #        "increment_prob[{}] + decrement_prob[{}] = {} + {} <= 0".format(
        #            i, i, increment_prob[i], decrement_prob[i]
        #        )
        for i, (h,c) in enumerate(zip(state_entropy, state_count)):
            state_entropy[i] = h/c

        for i, (inc, c) in enumerate(zip(increment_prob, state_count)):
            increment_prob[i] = inc/c

        for i, (unsat, c) in enumerate(zip(unsat_clauses, state_count)):
            unsat_clauses[i] = unsat/c

        # calculate the maximum number of measured states
        total_num_states = sum(
            map(
                lambda i: path_count(i) * (n - 2*i + 1),
                range(1, n // 2 + 1)
            )
        )

        return dict(
            formula_id=f_id,
            measured_states=len(measured_states),
            max_measured_states=total_num_states,
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
            unsat_clauses=[
                dict(hamming_dist=d, unsat_clauses=u)
                for d, u in enumerate(unsat_clauses)
            ]
        )
