import seaborn
import numpy
import math
import os

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE
from src.analysis.state_entropy import get_state_entropy_to_hamming_dist

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)

def plot_hamming_dist_to_state_entropy(
        filepath,
        solvers,
        outfile=DEFAULT_OUTFILE,
        figsize=(10, 3),
        verbose=False,
    ):
    xlim=[0,512]

    solver_folders = dict(
        walksat='WalkSAT',
        probsat='ProbSAT',
        gsat='GSAT',
    )

    labels = dict(
        state_entropy=r'$\overline{H\!\parens{Q_A | F}}$',
        hamming_dist=r'$d\!\parens{alpha^*, A}$',
    )

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
        for noise in noises:
            file = os.path.join(filepath, solver_folders[solver], f'{solver}-{noise}.db')
            if verbose:
                print(f'Loading from {file}... ', end='', flush=True)
            data = get_state_entropy_to_hamming_dist(file)
            if verbose:
                print('Done.')

            ax=axes[y]
            #seaborn.scatterplot(
            #    x='hamming_dist',
            #    y='state_entropy',
            #    data=data,
            #    marker='+',
            #    ax=ax,
            #)
            seaborn.lineplot(
                x='hamming_dist',
                y='state_entropy',
                data=data,
                label=f'${noise}$',
                ax=ax,
                estimator=numpy.mean,
            )
            ax.set_xlabel(labels['hamming_dist'])
            ax.set_ylabel(labels['state_entropy'])

    seaborn.despine()
    fig.savefig(outfile, bbox_inches='tight')
