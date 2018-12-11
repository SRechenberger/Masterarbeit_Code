import numpy as np
import numpy.linalg as la
from scipy.special import binom
from scipy.optimize import minimize
from scipy.stats import beta
from src.experiment.utils import eta
import sqlite3
import seaborn as sns
import math

#def eta(p):
#    print(p)
#    if p  <= 0:
#        return 0
#    elif p >= 1:
#        return 0
#    else:
#        return -p * math.log(p,2)

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
        # TODO something is mixed up here
        Pi[i][max(0,i-1)] = 1-p
        Pi[i][min(i+1,n-1)] = p

    return Pi


def approximate_stationary_distr(distr, eps=0.0001):
    assert type(eps) == float,\
        "eps = {} :: {} is no float".format(eps, type(eps))
    assert eps > 0,\
        "eps = {} <= 0".format(eps)

    # initiate transition matrix
    Pi = build_transition_matrix(distr)
    A = binomial_vec(len(distr))

    # approximate stationary distribution
    while True:
        # calculate new tmp
        T = A
        A = A @ Pi

        if la.norm(T - A) <= eps:
            break

    return A


def calculate_tms_entropy(distr_seq, eps = 0.0001):
    distr = np.array(distr_seq)
    A_inf = approximate_stationary_distr(distr, eps=eps)

    # calculate state entropy
    H = np.array([bin_h(p) for p in distr])

    # calculate entropy rate
    h = np.inner(H, A_inf)
    return h


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

def get_tms_entropy(file, experiment_id, eps=0.0001):
    for formula_file, distr in read_improvement_probs(file, experiment_id):
        yield formula_file, calculate_tms_entropy(distr, eps)


def log_likelihood(sample, pdf):
    n = len(sample)
    return sum(map(pdf, sample))/n


def fit_pdf(sample, pdf, n, bounds=None):
    theta = np.random.rand(n)
    f = lambda theta: log_likelihood(
            sample,
            lambda x: -pdf(x, *theta)
        )
    return minimize(
        f, theta,
        bounds=bounds,
    )
