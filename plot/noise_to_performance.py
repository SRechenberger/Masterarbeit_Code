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
        avg_runtime=r'$T_F$',
        avg_sat=r'$\prob{\mbox{„Erfolg“}}$',
    )
    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': ':'})
    seaborn.set_context('paper')
    fig, ((ax11,ax12),(ax21,ax22)) = pyplt.subplots(2, 2, figsize=(11,11))
    axes={
        ('WalkSAT', 'avg_runtime'): ax11,
        ('WalkSAT', 'avg_sat'): ax21,
        ('ProbSAT', 'avg_runtime'): ax12,
        ('ProbSAT', 'avg_sat'): ax22
    }

    for solver in solvers:
        data = path_entropy.noise_to_performance(
            os.path.join(in_filepath, solver),
            verbose
        )
        for metric in ['avg_runtime', 'avg_sat']:
            ax = axes[solver, metric]
            ax.set_xlim(xlims[solver])
            seaborn.lineplot(
                x='noise_param',
                y=metric,
                data=data,
                marker='o',
                ax=ax,
                estimator=numpy.mean,
                legend='full',
               # err_style='bars',
            )

            g = data.groupby('noise_param').apply(numpy.mean)
            opt_metric_value = (g.max() if metric == 'avg_sat' else g.min())[metric]
            opt_param_value = g.loc[g[metric] == opt_metric_value, 'noise_param'].values[0]
            ax.axvline(
                x=opt_param_value,
                label=opt_value[solver] + f'$ = {opt_param_value:.1f}$',
                color='r',
                linestyle=':',
            )


            ax.set_xlabel(opt_value[solver])
            ax.set_ylabel(metric_label[metric])
            ax.legend(loc='upper right')

    seaborn.despine()
    fig.savefig(outfile)
