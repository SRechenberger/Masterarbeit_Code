import sqlite3
import pandas
import os

import numpy as np


def path_entropy_to_performance(file, entropy, field):
    with sqlite3.connect(file) as conn:
        rows = conn.cursor().execute(
            f""" SELECT formula_id, {field}, sat, total_runtime \
            FROM algorithm_run NATURAL JOIN search_run JOIN entropy_data ON {entropy} = data_id \
            """
        )
        results = []
        for f_id, avg_h, avg_sat, avg_rt in rows:
            results.append((f_id, avg_h, avg_sat, avg_rt))

        return pandas.DataFrame.from_records(
            results,
            columns=['formula_id', 'value', 'avg_sat', 'avg_runtime']
        )


def noise_param_to_path_entropy(folder, solver, entropy, field):
    params = dict(
        gsat=('gsat.db', np.array(0)),
        walksat=('walksat-{:.2f}.db', np.concatenate(([], np.arange(0, 1.1, 0.1)))),
        probsat=('probsat-cb{:.1f}.db', np.concatenate(([2.3], np.arange(0, 4.1, 0.2)))),
    )

    template, args = params[solver]
    files = [(arg, os.path.join(folder, template.format(arg))) for arg in args]

    results = []

    for arg, file in files:
        #print(file)
        with sqlite3.connect(file, timeout=30) as conn:
            rows = conn.cursor().execute(
                f""" SELECT formula_id, avg({field}), sat, total_runtime \
                FROM algorithm_run NATURAL JOIN search_run JOIN entropy_data ON {entropy} = data_id \
                GROUP BY formula_id \
                """
            )
            for f_id, avg_v, sat, rt in rows:
                results.append((arg, f_id, avg_v, sat, rt))
    return pandas.DataFrame.from_records(
        results,
        columns=['noise_param', 'formula_id', 'value', 'sat', 'runtime']
    )
