import sqlite3
import pandas
import os
import sys

import numpy as np

from functools import partial

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


def noise_to_performance(folder, verbose=False):
    results = []
    files = map(partial(os.path.join, folder), os.listdir(folder))
    for file in files:
        if verbose:
            print(f'Loading Perfomance from {file}')

        try:
            with sqlite3.connect(file, timeout=30) as conn:
                rows = conn.cursor().execute(f""" \
                    SELECT
                        noise_param, \
                        formula_id, \
                        sat, \
                        total_runtime \
                    FROM experiment NATURAL JOIN algorithm_run \
                    """
                )
        except sqlite3.OperationalError as e:
            print(f'Skipped file {file} because of: {e}', file=sys.stderr)
            continue

        for noise_param, formula_id, sat, runtime in rows:
            results.append(
                (
                    noise_param,
                    formula_id,
                    runtime * (1 if sat else 10),
                )
            )


    return pandas.DataFrame.from_records(
        results,
        columns=[
            'noise_param',
            'formula_id',
            'runtime',
        ]
    )


def noise_param_to_path_entropy(folder, entropy, field, verbose=False):
    results = []
    files = map(partial(os.path.join, folder), os.listdir(folder))
    for file in files:
        if verbose:
            print(f"Loading from {file}")
        with sqlite3.connect(file, timeout=30) as conn:
            try:
                rows = conn.cursor().execute(
                    f"""
                    WITH average_runtime AS (
                        SELECT formula_id, avg(sat) as sat_avg, avg(total_runtime) as rt_avg
                        FROM algorithm_run
                        GROUP BY formula_id
                    ),
                    average_entropy AS (
                        SELECT noise_param, formula_id, avg({field}) as entropy_avg
                        FROM experiment
                            NATURAL JOIN algorithm_run
                            NATURAL JOIN search_run
                            JOIN entropy_data ON {entropy} = data_id
                        GROUP BY formula_id
                    )
                    SELECT noise_param, formula_id, entropy_avg, sat_avg, rt_avg
                    FROM average_entropy NATURAL JOIN average_runtime
                    """
                )
            except sqlite3.OperationalError as e:
                print(f'Skipped file {file} because of: {e}', file=sys.stderr)
                continue

            for row in rows:
                results.append(row)

    return pandas.DataFrame.from_records(
        results,
        columns=[
            'noise_param',
            'formula_id',
            'avg_value',
            'avg_sat',
            'avg_runtime'
        ]
    )
