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

def plot_noise_to_entropy_overview(
        in_filepath,
        outfile=DEFAULT_OUTFILE,
        field='average',
        figsize=(10,12),
        verbose=False):
    solvers = ['WalkSAT', 'ProbSAT']
    xlims = dict(
        WalkSAT=[0,1],
        ProbSAT=[0,4],
    )
    ylims = dict(
        single_entropy=[3, 8],
        joint_entropy=[5, 9.5],
        cond_entropy=[1, 4],
        mutual_information=[0,7],
    )
    opt_value = dict(
        WalkSAT=(r'$\rho$', 0.4),
        ProbSAT=(r'$c_b$', 2.6),
    )
    metric_label = dict(
        single_entropy=r'H_1',
        joint_entropy=r'H_2',
        cond_entropy=r'H_c',
        mutual_information=r'I',
    )
    metrics = ['single_entropy', 'joint_entropy', 'cond_entropy', 'mutual_information']
    # load data

    all_data = load_dynamic_data(in_filepath, field, solvers, verbose=verbose)

    # plot data
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
        data = all_data[solver]
        for x, metric in enumerate(metrics):
            # Scatterplot, if x1 == x2
            ax = axes[x][y]
            ax.set_xlim(xlims[solver])
            ax.set_ylim(ylims[metric])
            seaborn.scatterplot(
                x='noise_param',
                y=metric,
                data=data,
                # marker='o',
                ax=ax,
                alpha=0.8,
            )
            ax.axvline(
                x=opt_value[solver][1],
               # label=opt_value[solver][0],
                color='g',
                linestyle=':'
            )
            at_opt_mean = data['noise_param'] == opt_value[solver][1]
            opt_mean = numpy.mean(data[at_opt_mean][metric])
            ax.axhline(
                y=opt_mean,
                label=f'${metric_label[metric]} = {opt_mean:.3f}$',
                color='r',
                linestyle=':'
            )
            # Average lineplot in any case
            seaborn.lineplot(
                x='noise_param',
                y=metric,
                data=data,
                estimator=numpy.mean,
                ax=ax,
               # label='Mittelwert',
                color='g'
            )
            ax.set_xlabel(opt_value[solver][0])
            if solver == 'WalkSAT':
                ax.set_ylabel(f'${metric_label[metric]}$')
            else:
                ax.set_ylabel('')
                ax.yaxis.set_major_formatter(pyplt.NullFormatter())

    seaborn.despine()
    fig.savefig(outfile, bbox_inches='tight')
