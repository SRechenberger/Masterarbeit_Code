""" Module src.analysis.tms_entropy

Constants:
    CREATE_TMS_ENTROPY
    SAVE_TMS_ENTROPY

Functions:
    add_tms_entropy
"""


import sqlite3

import src.analysis.utils as utils

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

def add_tms_entropy(file, eps_exp=20, max_loops=20000):
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
        for series_id, in series_ids:
            print(series_id)
            test = conn.cursor().execute(
                "SELECT tms_entropy_id FROM tms_entropy WHERE series_id = ?",
                (series_id,)
            )
            if list(test):
                continue
            probs = conn.cursor().execute(
                "SELECT prob FROM improvement_probability WHERE series_id = ?",
                (series_id,)
            )
            tms_entropy, converged = utils.calculate_tms_entropy(
                list(probs),
                eps=2**-eps_exp,
                max_loops=max_loops
            )
            print(tms_entropy)
            conn.cursor().execute(
                SAVE_TMS_ENTROPY,
                (series_id, tms_entropy, converged, eps_exp, max_loops)
            )
        conn.commit()
