import sqlite3
import math
import pandas

import numpy as np
import numpy.linalg as la

from scipy.special import binom
from scipy.optimize import minimize
from scipy.stats import beta

from src.experiment.utils import eta

class StdevFunc:
    def __init__(self):
        self.values = []

    def step(self, value):
        self.values.append(value)

    def finalize(self):
        return np.std(self.values)


def flatten(xss):
    return [
        x
        for xs in xss
        for x in xs
    ]


def bin_h(p):
    return eta(p) + eta(1-p)


def binomial_vec(length):
    return np.array([binom(length-1,x) / 2**(length-1) for x in range(0,length)])


def build_transition_matrix(distr):
    n = len(distr)
    Pi = np.zeros((n,n))
    for i, p in enumerate(distr):
        Pi[i][max(0,i-1)] = p       # lower Hamming-distance => better
        Pi[i][min(i+1,n-1)] = 1 - p # higher Hamming-distance => worse

    return Pi


def approximate_stationary_distr(distr, eps=2**(-15), max_loops=20000):
    assert type(eps) == float,\
        "eps = {} :: {} is no float".format(eps, type(eps))
    assert eps > 0,\
        "eps = {} <= 0".format(eps)

    # initiate transition matrix
    Pi = build_transition_matrix(distr)
    A = binomial_vec(len(distr))

    # approximate stationary distribution
    for _ in range(max_loops):
        # calculate new tmp
        T = A
        A = A @ Pi

        if la.norm(T - A) <= eps:
            return A, True

    return A, False


def calculate_tms_entropy(distr_seq, **approx_kargs):
    distr = np.array(distr_seq)
    A_inf, converged = approximate_stationary_distr(distr, **approx_kargs)

    # calculate state entropy
    H = np.array([bin_h(p) for p in distr])

    # calculate entropy rate
    h = np.inner(H, A_inf)
    return h, converged


def read_improvement_probs(file, experiment_id):
    """ Return the list of improvement probablities
    as a list of arrays, paired with the formula file path
    """

    with sqlite3.connect(file) as conn:
        series = conn.cursor()
        series.execute(
            "SELECT series_id, formula_file FROM measurement_series WHERE experiment_id = ?",
            (experiment_id,)
        )
        for series_id, formula_file in series:
            improvement_prob = conn.cursor()
            improvement_prob.execute(
                "SELECT prob FROM improvement_probability WHERE series_id = ?",
                (series_id,)
            )
            yield formula_file, np.array(flatten(improvement_prob))

def get_tms_entropy(file, experiment_id, **approx_kargs):
    for formula_file, distr in read_improvement_probs(file, experiment_id):
        tms_entropy, converged = calculate_tms_entropy(distr, **approx_kargs)
        yield formula_file, tms_entropy, converged


def get_state_entropy_points(file, experiment_id):
    """Return state entropy of all formulae with their respective hamming distance"""
    with sqlite3.connect(file) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT hamming_dist, entropy_avg FROM measurement_series NATURAL JOIN state_entropy WHERE experiment_id = ?",
            (experiment_id,)
        )
        data_points = dict(
            hamming_dist=[],
            entropy_avg=[]
        )
        for hamming_dist, entropy_avg in cursor:
            data_points['hamming_dist'].append(hamming_dist)
            data_points['entropy_avg'].append(entropy_avg)

        return data_points


def get_state_entropy_distr(file, experiment_id):
    distr = {}
    points = get_state_entropy_points(file, experiment_id)
    for hamming_dist, entropy_avg in zip(points['hamming_dist'], points['entropy_avg']):
        if hamming_dist in distr:
            distr[hamming_dist].append(entropy_avg)
        else:
            distr[hamming_dist] = [entropy_avg]

    return distr



def get_entropy_avg(file, experiment_id, field):
    with sqlite3.connect(file) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT average FROM algorithm_run NATURAL JOIN search_run JOIN entropy_data ON {field} = data_id WHERE experiment_id = ? AND success = 1',
            (experiment_id,)
        )
        return np.array([h for h in cursor])


def hamming_dist_to_state_entropy(file, formula_id):
    with sqlite3.connect(file) as conn:
        rows = cursor.cursor().execute(
            """ SELECT experiment_id, hamming_dist, entropy_avg \
            FROM experiment \
                NATURAL JOIN measurement_series \
                NATURAL JOIN state_entropy \
            WHERE formula_id = ? """,
            (formula_id,),
        )

        return pandas.DataFrame.from_record(
            data=list(rows),
            cols=['experiment_id','hamming_dist','state_entropy'],
        )


def hamming_dist_to_state_entropy_avg_and_stdev(file, formula_id):
    with sqlite3.connect(file) as conn:

        conn.create_aggregate('stdev', 1, StdevFunc)

        rows = conn.cursor().execute(
            """ SELECT hamming_dist, stdev(entropy_avg), avg(entropy_avg) \
            FROM experiment \
                NATURAL JOIN measurement_series \
                NATURAL JOIN state_entropy \
            WHERE measurement_series.formula_id = ? \
            GROUP BY hamming_dist """,
            (formula_id,),
        )

        return pandas.DataFrame.from_records(
            data=list(rows),
            columns=['hamming_dist','stdev', 'avg'],
        )


def tms_entropy(file, satisfies=None):
    with sqlite3.connect(file) as conn:
        cursor = conn.cursor()
        series_ids = cursor.execute(
            """ SELECT formula_id, series_id \
            FROM measurement_series """
        )
        results = dict(
            formula_id=[],
            tms_entropy=[],
            converged=[],
        )
        for formula_id, series_id in series_ids:
            cursor_2 = conn.cursor()
            probs = cursor_2.execute(
                """ SELECT prob \
                FROM improvement_probability \
                WHERE series_id = ? """,
                (series_id,)
            )
            prob_vector = np.array([prob for prob in probs])
            tms_entropy, converged = calculate_tms_entropy(prob_vector)
            if not satisfies or satisfies(formula_id, tms_entropy, converged):
                results['formula_id'].append(formula_id)
                results['tms_entropy'].append(tms_entropy)
                results['converged'].append(converged)

        return pandas.DataFrame.from_dict(results)


def latest_entropy(file, field, satisfies=None):
    with sqlite3.connect(file) as conn:
        cursor = conn.cursor()
        run_ids = cursor.execute(
            """ SELECT formula_id, run_id \
            FROM algorithm_run \
            WHERE sat = 1 \
            """
        )
        results = dict(
            formula_id=[],
            run_id=[],
            success_entropy=[],
        )
        for formula_id, run_id in run_ids:
            success_entropy = conn.cursor().execute(
                f""" SELECT latest\
                FROM search_run JOIN entropy_data ON {field} = data_id \
                WHERE run_id = ? AND success = 1 \
                """,
                (run_id,)
            )
            success_entropy = list(success_entropy)
            if len(success_entropy) > 0:
                (success_entropy,), = success_entropy
                results['formula_id'].append(formula_id)
                results['run_id'].append(run_id)
                results['success_entropy'].append(success_entropy)

        return pandas.DataFrame.from_dict(results)


def avg_entropy(file, field, satisfies=None):
    with sqlite3.connect(file) as conn:
        run_ids = conn.cursor().execute(
            f""" SELECT formula_id, run_id, search_id, sat, latest, minimum, maximum, average \
            FROM \
                algorithm_run \
                NATURAL JOIN search_run \
                JOIN entropy_data ON {field} = data_id
            """
        )

        results = filter(lambda row: not satisfies or satisfies(*row), run_ids)

        return pandas.DataFrame.from_records(
            data=results,
            columns=['formula_id', 'run_id', 'search_id', 'sat', 'latest', 'minimum', 'maximum', 'average'],
        )
