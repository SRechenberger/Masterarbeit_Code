import seaborn
import numpy
import math
import scipy
import pandas

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, load_dynamic_data

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
        complete=True):
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
    opt_value = dict(
        WalkSAT=(r'\rho', 0.4),
        ProbSAT=(r'c_b', 2.6),
    )
    metric_label = dict(
        single_entropy=r'H_1',
        joint_entropy=r'H_2',
        cond_entropy=r'H_c',
        mutual_information=r'I',
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
    seaborn.set_context('paper')

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

            seaborn.distplot(
                data[metric],
                label=r'$\mu = {:.2f}$, $\sigma = {:.2f}$, $\gamma = {:.2f}$, $D = {:.2f}$'.format(mu, sigma, gamma, D),
                fit=scipy.stats.skewnorm,
                ax=ax,
                kde=False,
                rug=True,
            )

            ax.set_xlabel(f'${metric_label[metric]}$')
            ax.legend(loc='upper left')

    seaborn.despine()

    fig.savefig(outfile, bbox_inches='tight')
