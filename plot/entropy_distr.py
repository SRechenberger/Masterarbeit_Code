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

def plot_entropy_distr(in_filepath, metric, outfile=DEFAULT_OUTFILE, field='average', verbose=False):
    solvers = ['GSAT', 'WalkSAT', 'ProbSAT']
    dirs = dict(
        GSAT='GSAT',
        WalkSAT='WalkSAT_Opt',
        ProbSAT='ProbSAT_Opt',
    )
    opt_value = dict(
        WalkSAT=(r'\rho', 0.4),
        ProbSAT=(r'c_b', 2.4),
    )
    metric_label = dict(
        single_entropy=r'$H_1$',
        joint_entropy=r'$H_2$',
        mutual_information=r'$I$',
    )
    # load data

    all_data = load_dynamic_data(
        in_filepath,
        field,
        dirs.values(),
        [metric],
        verbose=verbose
    )

    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')

    fig, axes = pyplt.subplots(1, 3, figsize=(12,6))
    for y, solver in enumerate(solvers):
        ax = axes[y]

        data = all_data[dirs[solver], metric]

        print(data.min())

        gamma, mu, sigma = scipy.stats.skewnorm.fit(data['avg_value'])
        D, p = scipy.stats.kstest(
            data['avg_value'],
            'skewnorm',
            (gamma, mu, sigma),
        )

        print(solver, D)


        seaborn.distplot(
            data['avg_value'],
            label=r'$\mu = {:.2f}$, $\sigma = {:.2f}$, $\gamma = {:.2f}$, $D = {:.2f}$'.format(mu, sigma, gamma, D),
            fit=scipy.stats.skewnorm,
            ax=ax,
        )

        ax.set_xlabel(f'${metric_label[metric]}$')
        ax.legend(loc='upper left')

    seaborn.despine()

    fig.savefig(outfile)
