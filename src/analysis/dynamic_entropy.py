import sqlite3
import pandas

import numpy as np


def path_entropy_to_performance(file, entropy, field, repeat_axis=None):
    with sqlite3.connect(file) as conn:
        rows = conn.cursor().execute(
            f""" SELECT formula_id, {field}, sat, total_runtime \
            FROM algorithm_run NATURAL JOIN search_run JOIN entropy_data ON {entropy} = data_id \
            """
        )
        results = []
        repeats = {}
        for f_id, avg_h, avg_sat, avg_rt in rows:
            if f_id in repeats:
                repeats[f_id] += 1
            else:
                repeats[f_id] = 0

            if repeat_axis is None or repeat_axis == repeats[f_id]:
                results.append((f_id, avg_h, avg_sat, avg_rt))

        return pandas.DataFrame.from_records(
            results,
            columns=['formula_id', 'value', 'avg_sat', 'avg_runtime']
        )

