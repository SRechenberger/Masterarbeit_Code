import seaborn
import numpy
import math
import os

import src.analysis.dynamic_entropy as path_entropy

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, load_dynamic_data

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)

def plot_noise_to_performance(in_filepath, outfile=DEFAULT_OUTFILE, verbose=False):
    solvers = ['WalkSAT', 'ProbSAT']
    xlims = dict(
        WalkSAT=[0,1],
        ProbSAT=[0,4],
    )
    opt_value = dict(
        WalkSAT=r'$\rho$',
        ProbSAT=r'$c_b$',
    )
    metric_label = dict(
        runtime=r'$T_F$',
        sat=r'$\prob{\mbox{„Erfolg“}}$',
    )
    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': ':'})
    seaborn.set_context('paper')
    fig, (ax11,ax12) = pyplt.subplots(1, 2, figsize=(10,5), sharey=True)
    axes={
        'WalkSAT': ax11,
        'ProbSAT': ax12,
    }

    for solver in solvers:
        data = path_entropy.noise_to_performance(
            os.path.join(in_filepath, solver),
            verbose
        )

        ax = axes[solver]
        ax.set_xlim(xlims[solver])
        seaborn.lineplot(
            x='noise_param',
            y='runtime',
            data=data,
            marker='o',
            ax=ax,
            estimator=numpy.mean,
            legend='full',
        )

        g = data.groupby('noise_param').apply(numpy.mean)
        opt_metric_value = g.min()['runtime']
        opt_param_value = g.loc[g['runtime'] == opt_metric_value, 'noise_param'].values[0]
        ax.axvline(
            x=opt_param_value,
            label=opt_value[solver] + f'$ = {opt_param_value:.1f}$',
            color='r',
            linestyle=':',
        )

        ax.set_xlabel(opt_value[solver])
        ax.set_ylabel(metric_label['runtime'])
        ax.legend(loc='upper right')

    seaborn.despine()
    fig.savefig(outfile)
