import sqlite3
import pandas
import math

import numpy as np
import numpy.linalg as la
import scipy.optimize as opt


def get_state_entropy_to_hamming_dist(file, formula=None):
    """Return state entropy of all formulae with their respective hamming distance"""
    with sqlite3.connect(file) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """ SELECT formula_id, hamming_dist, avg(entropy_avg) \
            FROM formula NATURAL JOIN measurement_series NATURAL JOIN state_entropy \
            WHERE num_vars > hamming_dist \
            GROUP BY formula_id, hamming_dist """,
        )
        results = []
        for formula_id, hamming_dist, entropy_avg in cursor:
            if not formula or formula_id == formula:
                results.append((formula_id, hamming_dist, entropy_avg))

        return pandas.DataFrame.from_records(
            results,
            columns=['formula_id', 'hamming_dist', 'state_entropy']
        )


def log_square(x, a, b, c, d):
    return -a*np.log((x+b)*c)**2 + d


def fit_state_entropy_avg_to_log_square(file):
    with sqlite3.connect(file) as conn:
        rows = conn.cursor().execute(
            """ SELECT hamming_dist, avg(entropy_avg) \
            FROM measurement_series NATURAL JOIN state_entropy \
            GROUP BY hamming_dist """
        )

        x_vals = []
        y_vals = []
        for d, h in rows:
            x_vals.append(d)
            y_vals.append(h)

        ds = np.array(x_vals)
        hs = np.array(y_vals)

        popt, _ = opt.curve_fit(
            log_square, ds, hs,
        )
        return popt


def get_state_entropy_avg_to_hamming_dist(file):
    with sqlite3.connect(file) as conn:
        rows = conn.cursor().execute(
            """ SELECT hamming_dist, avg(entropy_avg) \
            FROM formula NATURAL JOIN measurement_series NATURAL JOIN state_entropy \
            WHERE num_vars > hamming_dist \
            GROUP BY hamming_dist """
        )

        results = []
        for dist, entropy in rows:
            results.append((dist, entropy))

        return pandas.DataFrame.from_records(
            results[:-1],
            columns=['hamming_dist', 'entropy_avg']
        )


def get_unsat_clause_avg_to_hamming_dist(file):
    with sqlite3.connect(file) as conn:
        rows = conn.cursor().execute(
            """ SELECT hamming_dist, avg(unsat_clauses) \
            FROM formula NATURAL JOIN measurement_series NATURAL JOIN unsat_clauses \
            WHERE num_vars > hamming_dist \
            GROUP BY hamming_dist """
        )

        results = []
        for dist, unsat in rows:
            results.append((dist, unsat))

        return pandas.DataFrame.from_records(
            results[:-1],
            columns=['hamming_dist', 'unsat_clauses']
        )

def get_unsat_clause_to_hamming_dist(file):
    with sqlite3.connect(file) as conn:
        rows = conn.cursor().execute(
            """ SELECT hamming_dist, unsat_clauses \
            FROM formula NATURAL JOIN measurement_series NATURAL JOIN unsat_clauses \
            WHERE num_vars > hamming_dist \
            """
        )

        results = []
        for dist, unsat in rows:
            results.append((dist, unsat))

        return pandas.DataFrame.from_records(
            results[:-1],
            columns=['hamming_dist', 'unsat_clauses']
        )
