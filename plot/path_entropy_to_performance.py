import seaborn
import numpy
import math

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, load_runtime_to_entropy

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)

def plot_path_entropy_to_performance(
        in_filepath,
        outfile=DEFAULT_OUTFILE,
        field='average',
        figsize=(10, 12),
        verbose=False
    ):
    solvers = ['GSAT', 'WalkSAT_Opt', 'ProbSAT_Opt']
    metrics = ['single_entropy', 'joint_entropy', 'cond_entropy', 'mutual_information']

    metric_label = dict(
        single_entropy=r'$H_1$',
        joint_entropy=r'$H_2$',
        cond_entropy=r'$H_c$',
        mutual_information=r'$I$',
    )

    # load data
    all_data = load_runtime_to_entropy(in_filepath, field, solvers, verbose=verbose)

    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')
    fig, axes = pyplt.subplots(
        len(metrics),
        len(solvers),
        sharey=True,
        figsize=figsize,
    )
    fig.tight_layout()
    for y, solver in enumerate(solvers):
        data = all_data[solver]
        for x, metric in enumerate(metrics):

            ax = axes[x][y]
            seaborn.scatterplot(
                x=metric,
                y='runtime',
                data=data,
                marker='o',
                ax=ax,
            )
            opt_mean = numpy.mean(data[metric])
            ax.axvline(
                x=opt_mean,
                # label=r'$\expect{h}=' + f'{opt_mean:.3f}$',
                color='r',
                linestyle=':'
            )
            ax.set_xlabel(r'\Large' + metric_label[metric])
            ax.set_ylabel(r'\Large $\expect{T_f}$')

    seaborn.despine()

    fig.savefig(outfile, bbox_inches='tight')
