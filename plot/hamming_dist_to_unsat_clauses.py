import seaborn
import numpy
import math
import os
import pandas
import sys

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE
from src.analysis.state_entropy import get_unsat_clause_to_hamming_dist

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)

def plot_hamming_dist_to_unsat_clauses(
        files,
        outfile=DEFAULT_OUTFILE,
        figsize=(5, 3),
        verbose=False,
    ):

    xlim=[0,512]

    labels = dict(
        hamming_dist=r'$\frac{d\!\parens{\alpha^*, A}}{N_F}$',
        unsat_clauses=r'$\card{\unsat{F}{A}}$',
    )

    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')

    fig, ax = pyplt.subplots(
        1,
        1,
        figsize=figsize,
        sharex=True,
        sharey=True,
    )
    fig.tight_layout()

    dfs = []
    for file in files:
        if verbose:
            print(f'Loading from {file}... ', end='', flush=True)

        dfs.append(get_unsat_clause_to_hamming_dist(file))
        if verbose:
            print('Done.')

    data = pandas.concat(dfs)

    data = data.groupby(['hamming_dist'], as_index=False).mean()
    max_unsat_clauses = max(data['unsat_clauses'])
    x_extr = data[data['unsat_clauses'] == max_unsat_clauses]['hamming_dist'].iloc[0]

    data['hamming_dist'] = data['hamming_dist'] / 512
    data['unsat_clauses'] = data['unsat_clauses']

    seaborn.lineplot(
        x='hamming_dist',
        y='unsat_clauses',
        data=data,
        ax=ax,
        estimator=numpy.mean,
    )
    ax.axvline(
        x=x_extr/512,
        linestyle=':',
        color='g',
    )

    ax.set_xlabel(labels['hamming_dist'])
    ax.set_ylabel(labels['unsat_clauses'])

    seaborn.despine()
    fig.savefig(outfile, bbox_inches='tight')
