import seaborn
import numpy
import math
import os

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, LABELS, SOLVER_LABELS
from src.analysis.state_entropy import get_state_entropy_to_hamming_dist

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)

def plot_hamming_dist_to_state_entropy(
        filepath,
        type_idx,
        outfile=DEFAULT_OUTFILE,
        figsize=(10, 3),
        verbose=False,
    ):
    xlim=[0,512]
    types = {
        0: dict(
            gsat=[0],
            walksat=[0.4, 0.57, 0.0, 1.0],
            probsat=[2.6, 2.3, 0.0, 4.0],
        ),
        1: dict(
            walksat=[0.0, 0.4, 0.57, 1.0],
            probsat=[0.0, 2.3, 2.6, 4.0],
        ),

    }

    solvers = types[type_idx]

    if type_idx in [0]:
        entropy_label = LABELS['state_entropy']

    elif type_idx in [1]:
        entropy_label = LABELS['state_entropy_square']

    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')

    fig, axes = pyplt.subplots(
        1,
        len(solvers),
        figsize=figsize,
        sharex=True,
        sharey=True,
    )
    fig.tight_layout()

    for y, (solver, noises) in enumerate(solvers.items()):
        ax=axes[y]
        line_drawn = False
        for noise in noises:
            file = os.path.join(filepath, SOLVER_LABELS[solver], f'{solver}-{noise}.db')
            if verbose:
                print(f'Loading from {file}... ', end='', flush=True)
            data = get_state_entropy_to_hamming_dist(file)
            if verbose:
                print('Done.')
            data['hamming_dist'] = data['hamming_dist'] / 512
            data['state_entropy'] = data['state_entropy'] * math.log(513, 2)
            if type_idx == 1:
                data['state_entropy'] = 2 ** data['state_entropy']


            if solver == 'gsat':
                noise_labels = dict()
            else:
                noise_labels = dict(
                    label=f'${LABELS[SOLVER_LABELS[solver]]} = {noise}$',
                )

            if not line_drawn:
                data = data.groupby(['hamming_dist'], as_index=False).mean()
                max_unsat_clauses = max(data['state_entropy'])
                x_extr = data[data['state_entropy'] == max_unsat_clauses]['hamming_dist'].iloc[0]
                ax.axvline(
                    x=x_extr,
                    linestyle=':',
                    color='g',
                    label=f'$d = {x_extr}$'
                )
                line_drawn = True

            seaborn.lineplot(
                x='hamming_dist',
                y='state_entropy',
                data=data,
                ax=ax,
                estimator=numpy.mean,
                **noise_labels
            )

            ax.set_xlabel(f'${LABELS["hamming_dist"]}$')
            ax.set_ylabel(f'${entropy_label}$')

    seaborn.despine()
    fig.savefig(outfile, bbox_inches='tight')
