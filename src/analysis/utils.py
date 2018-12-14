import numpy as np
import numpy.linalg as la
from scipy.special import binom
from scipy.optimize import minimize
from scipy.stats import beta
from src.experiment.utils import eta
import sqlite3
import seaborn as sns
import math

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


def approximate_stationary_distr(distr, eps=0.0001, max_loops=1000):
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
