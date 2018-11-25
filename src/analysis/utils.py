import numpy as np
from scipy.special import binom
from src.experiment.utils import eta


def bin_h(p):
    return eta(p) + eta(1-p)

def binomial_vec(length):
    return np.array([binom(length-1,x) / 2**(length-1) for x in range(0,length)])


def get_tms_entropy(distr_seq, eps = 0.001, max_loops = 10000):
    assert type(eps) == float,\
        "eps = {} :: {} is no float".format(eps, type(eps))
    assert eps > 0,\
        "eps = {} <= 0".format(eps)
    assert type(max_loops) == int,\
        "max_loops = {} :: {} is no int".format(max_loops, type(max_loops))
    assert max_loops > 0,\
        "max_loops = {} <= 0".format(max_loops)


    distr = np.array(distr_seq)
    # get number of states
    tms_states = len(distr)

    # initiate initial distribution
    T_0 = binomial_vec(tms_states)

    # initiate transition matrix
    Pi = np.zeros((tms_states,tms_states))


    ## build transition matrix
    for i,p in enumerate(distr):
        Pi[i][max(0,i-1)] = 1-distr[i]
        Pi[i][min(i+1,n)] = 1-distr[i]

    # approximate stationary distribution
    T = T_0.copy()

    s = sum(distr)

    loops = 0
    converging = 0
    while loops < 100 or (converging < len(distr) and loops < max_loops):
        # calculate new tmp
        Tmp = T @ Pi

        converging = 0
        for (t,tmp) in zip(T,Tmp):
            if abs(d-t) <= eps:
                converging += 1

        # save new tmp
        T = tmp

        # next loop
        loops += 1


    # calculate state entropy
    state_entropy = np.array([bin_h(p) for p in distr])

    # calculate entropy rate
    h = np.inner(state_entropy, T)
    return h
