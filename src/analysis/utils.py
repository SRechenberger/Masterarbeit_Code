"""
## Module src.analysis.utils

### Contents
    - class StdevFunc
    - function bin_h
    - function binomial_vec
    - function approximate_stationary_distr
    - function calculate_tms_entropy
"""

import numpy as np
import numpy.linalg as la

from scipy.special import binom

from src.experiment.utils import eta


def bin_h(p):
    """ Binary Shannon Entropy """
    return eta(p) + eta(1-p)


def binomial_vec(length):
    """ Binomial distribution vector """
    return np.array([binom(length-1, x) / 2**(length-1) for x in range(0, length)])


def build_transition_matrix(distr):
    """ Construct the TMS transition matrix from improvement probabilities """
    n = len(distr)
    Pi = np.zeros((n, n))
    for i, p in enumerate(distr):
        Pi[i][max(0, i-1)] = p       # lower Hamming-distance => better
        Pi[i][min(i+1, n-1)] = 1 - p # higher Hamming-distance => worse

    return Pi


def approximate_stationary_distr(distr, eps=2**(-15), max_loops=20000):
    """ Approximate the stationary distribution of a markov chain """
    assert isinstance(eps, float),\
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
    """ Calculate the TMS entropy """
    distr = np.array(distr_seq)
    A_inf, converged = approximate_stationary_distr(distr, **approx_kargs)

    # calculate state entropy
    H = np.array([bin_h(p) for p in distr])

    # calculate entropy rate
    h = np.inner(H, A_inf)
    return h, converged
