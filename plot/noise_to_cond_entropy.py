import seaborn
import numpy
import math

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, load_dynamic_data

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)


def plot_noise_to_cond_entropy(in_filepath, figsize=(10,5), outfile=DEFAULT_OUTFILE, field='average', verbose=False):
    solvers = ['WalkSAT', 'ProbSAT']
    xlims = dict(
        WalkSAT=[0,1],
        ProbSAT=[0,4],
    )
    opt_value = dict(
        WalkSAT=(r'$\rho$', 0.4),
        ProbSAT=(r'$c_b$', 2.4),
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
        solvers,
        ['joint_entropy', 'single_entropy'],
        verbose=verbose
    )


    # plot data
    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')
    fig, axes = pyplt.subplots(1, 2, sharey=True, figsize=figsize)
    fig.tight_layout()
    for y, solver in enumerate(solvers):

        # Scatterplot, if x1 == x2
        ax = axes[y]
       # ax.set_xlim(xlims[solver])
        H1 = all_data[solver, 'single_entropy']
        H2 = all_data[solver, 'joint_entropy']

        H2['cond_entropy'] = H2['avg_value'] - H1['avg_value']

        seaborn.scatterplot(
            x='noise_param',
            y='cond_entropy',
            data=H2,
            #marker='+',
            ax=ax,
        )
        seaborn.lineplot(
            x='noise_param',
            y='cond_entropy',
            data=H2,
            estimator=numpy.mean,
            ax=ax,
            label='Mittelwert',
            color='g'
        )
        ax.set_xlabel("X")#opt_value[solver][0])
        ax.set_ylabel("Y")#f'$\\frac{metric_label["mutual_information"]}{metric_label["joint_entropy"]}$')

    seaborn.despine()

    fig.savefig(outfile, bbox_inches='tight')
