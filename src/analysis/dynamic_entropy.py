import sqlite3
import pandas
import os
import sys

import numpy as np

from functools import partial

def path_entropy_to_runtime(folder, field, verbose=False):
    results = []
    files = map(partial(os.path.join, folder), os.listdir(folder))
    for file in files:
        try:
            with sqlite3.connect(file) as conn:
                rows = conn.cursor().execute(
                    f"""
                    WITH entropies AS
                        (SELECT
                            run_id,
                            formula_id,
                            sat,
                            total_runtime,
                            avg(h1.{field}) as h1,
                            avg(h2.{field}) as h2,
                            avg(h3.{field}) as hc,
                            avg(h4.{field}) as i
                        FROM algorithm_run
                            NATURAL JOIN search_run
                            JOIN entropy_data h1 ON single_entropy = h1.data_id
                            JOIN entropy_data h2 ON joint_entropy = h2.data_id
                            JOIN entropy_data h3 ON cond_entropy = h3.data_id
                            JOIN entropy_data h4 ON mutual_information = h4.data_id
                        GROUP BY
                            run_id)
                    SELECT
                        formula_id,
                        avg(sat),
                        avg(total_runtime),
                        avg(h1),
                        avg(h2),
                        avg(hc),
                        avg(i)
                    FROM entropies
                    GROUP BY formula_id
                    """
                )

        except sqlite3.OperationalError as e:
            print(f'Skipped file {file} because of: {e}', file=sys.stderr)
            continue

        for f_id, avg_sat, avg_rt, *avg_hs in rows:
            results.append((
                f_id,
                (10 * (1-avg_sat) if avg_sat < 1 else 1) * avg_rg,
                *avg_hs
            ))

    return pandas.DataFrame.from_records(
        results,
        columns=[
            'formula_id',
            'runtime',
            'single_entropy',
            'joint_entropy',
            'cond_entropy',
            'mutual_information'
        ]
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


def noise_param_to_path_entropy(folder, field, verbose=False):
    results = []
    files = map(partial(os.path.join, folder), os.listdir(folder))
    for file in files:
        if verbose:
            print(f"Loading from {file}")
        with sqlite3.connect(file, timeout=30) as conn:
            try:
                rows = conn.cursor().execute(
                    f"""
                    SELECT
                        noise_param,
                        formula_id,
                        avg(h1.{field}) as single_entropy,
                        avg(h2.{field}) as joint_entropy,
                        avg(h3.{field}) as cond_entropy,
                        avg(h4.{field}) as mutual_information
                    FROM
                        experiment
                        NATURAL JOIN algorithm_run
                        NATURAL JOIN search_run
                        JOIN entropy_data h1 ON single_entropy = h1.data_id
                        JOIN entropy_data h2 ON joint_entropy = h2.data_id
                        JOIN entropy_data h3 ON cond_entropy = h3.data_id
                        JOIN entropy_data h4 ON mutual_information = h4.data_id
                    GROUP BY formula_id
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
            'single_entropy',
            'joint_entropy',
            'cond_entropy',
            'mutual_information',
        ]
    )
