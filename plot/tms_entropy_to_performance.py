import seaborn
import numpy
import math

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, load_from_all_subfolders
from src.analysis.tms_entropy import tms_entropy_to_performance

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)

def plot_tms_entropy_to_performance(
        in_filepath,
        outfile=DEFAULT_OUTFILE,
        figsize=(10, 12),
        verbose=False,
    ):
    solvers = ['GSAT', 'WalkSAT_Opt', 'ProbSAT_Opt']

    figsize = (
        figsize[0],
        figsize[1],
    )

    solver_label = dict(
        GSAT='GSAT',
        WalkSAT_Opt='WalkSAT',
        ProbSAT_Opt='ProbSAT',
    )

    labels = dict(
        tms_entropy=r'$\hat H\!\parens{M_F}$',
        runtime=r'$\overline{T_F}$',
    )

    # load data
    all_data = load_from_all_subfolders(
        tms_entropy_to_performance,
        in_filepath,
        solvers,
        only_convergend=True,
        verbose=verbose,
    )

    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')
    fig, axes = pyplt.subplots(
        1,
        len(solvers),
        sharey=True,
        figsize=figsize,
    )
    fig.tight_layout()
    for y, solver in enumerate(solvers):
        data = all_data[solver]

        ax = axes[y]

        seaborn.scatterplot(
            x='tms_entropy',
            y='runtime',
           #  hue='converged',
            data=data,
            marker='+',
            alpha=0.9,
            ax=ax,
        )
        h_mean = numpy.mean(data['tms_entropy'])
        t_mean = numpy.mean(data['runtime'])
        ax.axvline(
            x=h_mean,
            # label=r'$\expect{h}=' + f'{opt_mean:.3f}$',
            color='r',
            linestyle=':'
        )
        ax.axhline(
            y=t_mean,
            # label=r'$\expect{h}=' + f'{opt_mean:.3f}$',
            color='g',
            linestyle=':'
        )
        ax.set_xlabel(labels['tms_entropy'])
        ax.set_ylabel(r'$\overline{T_F}$')

    seaborn.despine()

    fig.savefig(outfile, bbox_inches='tight')
