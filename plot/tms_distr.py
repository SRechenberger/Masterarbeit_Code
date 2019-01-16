import seaborn
import numpy
import math
import scipy
import pandas

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, load_noise_to_tms_entropy

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)

def plot_tms_distr(
        in_filepath,
        figsize=(10,12),
        outfile=DEFAULT_OUTFILE,
        verbose=False,
        context='paper',
        complete=True):
    solvers = ['GSAT', 'WalkSAT', 'ProbSAT']

    values = dict(
        GSAT=[0],
        WalkSAT=[0, 0.4, 0.57, 1.0],
        ProbSAT=[0, 2.3, 2.6, 4],
    )

    noise_labels=dict(
        GSAT=r'x',
        WalkSAT=r'\rho',
        ProbSAT=r'c_b',
    )

    metric_label = dict(
        tms_entropy='H\!\parens{M_F}',
    )
    # load data

    all_data = load_noise_to_tms_entropy(
        in_filepath,
        solvers,
        only_convergent=True,
        verbose=verbose,
    )

    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context(context)

    fig, axes = pyplt.subplots(
        4,
        len(solvers),
        figsize=figsize
    )
    fig.tight_layout()
    for y, solver in enumerate(solvers):
        data = all_data[solver]
        for x, noise_param in enumerate(values[solver]):
            ax = axes[x][y]
            tmp_data = data[data['noise_param'] == noise_param]

            gamma, mu, sigma = scipy.stats.skewnorm.fit(tmp_data['tms_entropy'])
           # D, p = scipy.stats.kstest(
           #     data['tms_entropy'],
           #     'skewnorm',
           #     (gamma, mu, sigma),
           # )

            seaborn.distplot(
                tmp_data['tms_entropy'],
                label=r'$\mu = {:.2f}$, $\sigma = {:.2f}$, $\gamma = {:.2f}$'.format(
                    mu, sigma, gamma
                ),
                fit=scipy.stats.skewnorm,
                ax=ax,
                kde=False,
                rug=True,
            )

            ax.set_xlabel(f'${metric_label["tms_entropy"]}$')
            ax.legend(loc='upper left')

    seaborn.despine()

    fig.savefig(outfile, bbox_inches='tight')
