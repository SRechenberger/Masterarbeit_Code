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

def plot_noise_to_entropy_overview(in_filepath, metric, outfile=DEFAULT_OUTFILE, field='average', verbose=False):
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
    metrics = ['single_entropy', 'joint_entropy', 'mutual_information']
    # load data

    all_data = load_dynamic_data(in_filepath, field, solvers, [metric], verbose=verbose)

    # plot data
    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')
    fig, axes = pyplt.subplots(1, 2, sharey=True, figsize=(10,5))
    for y, solver in enumerate(solvers):

        # Scatterplot, if x1 == x2
        ax = axes[y]
        ax.set_xlim(xlims[solver])
        data = all_data[solver, metric]
        seaborn.scatterplot(
            x='noise_param',
            y='avg_value',
            data=data,
            # marker='o',
            ax=ax,
            alpha=0.8,
        )
        ax.axvline(
            x=opt_value[solver][1],
            label=opt_value[solver][0],
            color='g',
            linestyle=':'
        )
        at_opt_mean = data['noise_param'] == opt_value[solver][1]
        opt_mean = numpy.mean(data[at_opt_mean]['avg_value'])
        ax.axhline(
            y=opt_mean,
            label=r'$\expect{h}=' + f'{opt_mean:.3f}$',
            color='r',
            linestyle=':'
        )
        # Average lineplot in any case
        seaborn.lineplot(
            x='noise_param',
            y='avg_value',
            data=data,
            estimator=numpy.mean,
            ax=ax,
            label='Mittelwert',
            color='g'
        )
        ax.set_xlabel(opt_value[solver][0])
        ax.set_ylabel(metric_label[metric])

    seaborn.set_style('whitegrid')
    seaborn.set_context('paper')
    seaborn.despine()

    fig.savefig(outfile)
