""" Module src.analysis.tms_entropy

Constants:
    CREATE_TMS_ENTROPY
    SAVE_TMS_ENTROPY

Functions:
    add_tms_entropy
"""

import os
import sqlite3
import pandas

import numpy as np
import multiprocessing as mp

import src.analysis.utils as utils

from functools import partial

CREATE_TMS_ENTROPY = """
CREATE TABLE IF NOT EXISTS tms_entropy
    ( tms_entropy_id    INTEGER PRIMARY KEY
    , series_id         INTEGER NOT NULL
    , value             REAL NOT NULL
    , converged         BOOL NOT NULL
    , eps_exp           INTEGER NOT NULL
    , max_loops         INTEGER NOT NULL
    , FOREIGN KEY(series_id) REFERENCES measurement_series(series_id)
    )
"""

SAVE_TMS_ENTROPY = """
INSERT INTO tms_entropy
    ( series_id
    , value
    , converged
    , eps_exp
    , max_loops
    )
VALUES (?,?,?,?,?)
"""

UPDATE_TMS_ENTROPY = """
UPDATE tms_entropy
SET value = ?, converged = ?, eps_exp = ?, max_loops = ?
WHERE series_id = ?
"""

def add_tms_entropy(file, eps_exp=15, max_loops=10000, update=True, poolsize=3):
    """ Adds the table holding the TMS-entropy to the given database file

    Positionals:
        file: the database file, to modify

    Keywords:
        eps_exp: the exponent setting the tolerance for the approximation
                 of stationary distribution; eps = 2 ** -eps_exp
        max_loops: maximum number of iterations for appriximating the stationary distribution
    """
    with sqlite3.connect(file, timeout=30) as conn:
        conn.cursor().execute(CREATE_TMS_ENTROPY)
        series_ids = conn.cursor().execute(
            "SELECT series_id FROM measurement_series"
        )
        with mp.Pool(processes=poolsize) as pool:
            future_results = []
            updated_ids = set()
            for series_id, in series_ids:
                test = conn.cursor().execute(
                    "SELECT eps_exp, max_loops FROM tms_entropy WHERE series_id = ?",
                    (series_id,)
                )
                test = list(test)
                if test and update:
                    updated_ids.add(series_id)
                elif test:
                    continue

                probs = conn.cursor().execute(
                    "SELECT prob FROM improvement_probability WHERE series_id = ?",
                    (series_id,)
                )
                future_result = pool.apply_async(
                    partial(utils.calculate_tms_entropy, eps=2**-eps_exp, max_loops=max_loops),
                    (
                        list(probs),
                    )
                )
                future_results.append((series_id, future_result))

            for result in [(series_id, *result.get()) for (series_id, result) in future_results]:
                series_id, tms_entropy, converged = result
                if series_id in updated_ids:
                    conn.cursor().execute(
                        UPDATE_TMS_ENTROPY,
                        (tms_entropy, converged, eps_exp, max_loops, series_id)
                    )
                else:
                    conn.cursor().execute(
                        SAVE_TMS_ENTROPY,
                        (series_id, tms_entropy, converged, eps_exp, max_loops)
                    )
        conn.commit()


def tms_entropy_values(file, only_convergent=True, satisfies=None):
    """ Returns a DataFrame of the distribution of the TMS-entropy

    Positionals:
        file: Database file to read

    Keywords:
        only_convergent: if True, only the result of convergent values will be returned

    Returns:
        DataFrame having the columns ['solver', 'noise_param', 'formula_id', 'tms_entropy']
    """

    with sqlite3.connect(file, timeout=30) as conn:
        if only_convergent:
            query = """ \
                SELECT solver, noise_param, formula_id, value \
                FROM experiment NATURAL JOIN measurement_series NATURAL JOIN tms_entropy \
                WHERE converged = 1 \
            """
        else:
            query = """ \
                SELECT solver, noise_param, formula_id, value \
                FROM experiment NATURAL JOIN measurement_series NATURAL JOIN tms_entropy \
            """
        cursor = conn.cursor().execute(query)
        return pandas.DataFrame.from_records(
            list(filter(lambda args: satisfies(*args) if satisfies else True, cursor)),
            columns=['solver', 'noise_param', 'formula_id', 'tms_entropy']
        )


def tms_entropy_to_noise_param(folder, solver):
    params = dict(
        gsat=('gsat.db', np.array(0)),
        walksat=('walksat-rho{:.1f}.db', np.concatenate(([0.57], np.arange(0, 1.1, 0.1)))),
        probsat=('probsat-cb{:.1f}.db', np.concatenate(([2.3], np.arange(0, 4.1, 0.2)))),
    )

    template, args = params[solver]
    files = [(arg, os.path.join(folder, template.format(arg))) for arg in args]

    results = []

    for arg, file in files:
        with sqlite3.connect(file, timeout=30) as conn:
            entropies = conn.cursor().execute(
                "SELECT value, converged FROM tms_entropy"
            )
            for entropy, conv_rate in entropies:
                results.append((arg, entropy, conv_rate))

    return pandas.DataFrame.from_records(
        results,
        columns=['noise_param', 'tms_entropy', 'conv_rate']
    )

def tms_entropy_to_performance(file):
    with sqlite3.connect(file, timeout=30) as conn:
        rows = conn.cursor().execute(
            """ SELECT measurement_series.formula_id, avg(tms_entropy.converged), avg(tms_entropy.value), avg(algorithm_run.total_runtime), avg(algorithm_run.sat) \
            FROM tms_entropy NATURAL JOIN measurement_series JOIN algorithm_run ON measurement_series.formula_id = algorithm_run.formula_id \
            GROUP BY measurement_series.formula_id \
            """
        )
        results = []
        for f_id, avg_conv, tms_h, avg_rt, avg_succ in rows:
            results.append((f_id, avg_conv, tms_h, avg_rt, avg_succ))

        return pandas.DataFrame.from_records(
            results,
            columns=['formula_id', 'avg_converged', 'tms_entropy', 'avg_runtime', 'avg_sat']
        )

