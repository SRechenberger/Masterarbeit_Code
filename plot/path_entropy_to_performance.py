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

def plot_path_entropy_to_performance(in_filepath, metric, outfile=DEFAULT_OUTFILE, field='average', verbose=False):
    solvers = ['GSAT', 'WalkSAT_Opt', 'ProbSAT_Opt']
    metrics = ['single_entropy', 'joint_entropy', 'mutual_information']

    if metric not in metrics:
        raise RuntimeError(f'metric = {metric} not in {metrics}')

    opt_value = dict(
        WalkSAT_Opt=(r'$\rho$', 0.4),
        ProbSAT_Opt=(r'$c_b$', 2.4),
    )
    metric_label = dict(
        single_entropy=r'$H_1$',
        joint_entropy=r'$H_2$',
        mutual_information=r'$I$',
    )

    # load data
    all_data = load_dynamic_data(in_filepath, field, solvers, [metric], verbose=verbose)


    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')
    fig, axes = pyplt.subplots(1, 3, sharex=True, sharey=True)
    fig.tight_layout()
    for x, solver in enumerate(solvers):

        ax = axes[x]
        data = all_data[solver, metric]
        seaborn.scatterplot(
            x='avg_value',
            y='avg_runtime',
            data=data,
            marker='+',
            ax=ax,
        )
        opt_mean = numpy.mean(data['avg_value'])
        ax.axvline(
            x=opt_mean,
            label=r'$\expect{h}=' + f'{opt_mean:.3f}$',
            color='r',
            linestyle=':'
        )
        ax.set_xlabel(r'\Large' + metric_label[metric])
        ax.set_ylabel(r'\Large $\expect{T_f}$')

    seaborn.despine()

    fig.savefig(outfile, bbox_inches='tight')
