import seaborn
import numpy
import math
import scipy
import pandas

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, load_dynamic_data, LABELS

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)

def plot_entropy_distr(
        in_filepath,
        metrics,
        figsize=(10,12),
        outfile=DEFAULT_OUTFILE,
        field='average',
        verbose=False,
        complete=True,
        context='paper'):
    solvers = ['GSAT', 'WalkSAT', 'ProbSAT']

    figsize = (
        figsize[0],
        figsize[1]/4 * len(metrics),
    )

    dirs = dict(
        GSAT='GSAT',
        WalkSAT='WalkSAT_Opt',
        ProbSAT='ProbSAT_Opt',
    )
    # load data

    all_data = load_dynamic_data(
        in_filepath,
        field,
        dirs.values(),
        verbose=verbose
    )

    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context(context)

    fig, axes = pyplt.subplots(
        len(metrics),
        len(solvers),
        figsize=figsize
    )
    fig.tight_layout()
    for y, solver in enumerate(solvers):
        data = all_data[dirs[solver]]
        for x, metric in enumerate(metrics):
            ax = axes[x][y]

            gamma, mu, sigma = scipy.stats.skewnorm.fit(data[metric])
            D, p = scipy.stats.kstest(
                data[metric],
                'skewnorm',
                (gamma, mu, sigma),
            )
            if context == 'paper':
                lbl=r'$\mu = {:.2f}$, $\sigma = {:.2f}$, $\gamma = {:.2f}$, $D = {:.2f}$'.format(mu, sigma, gamma, D)
            else:
                lbl = r'${:.2f}$, ${:.2f}$, ${:.2f}$, ${:.2f}$'.format(mu, sigma, gamma, D)


            seaborn.distplot(
                data[metric],
                label=lbl,
                fit=scipy.stats.skewnorm,
                ax=ax,
                kde=False,
                rug=True,
            )

            ax.set_xlabel(f'${LABELS[metric]}$')
            ax.legend(loc='upper left')

    seaborn.despine()

    fig.savefig(outfile, bbox_inches='tight')
