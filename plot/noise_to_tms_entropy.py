import seaborn
import numpy
import math

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, load_noise_to_tms_entropy

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)

def plot_noise_to_tms_entropy(
        in_filepath,
        outfile=DEFAULT_OUTFILE,
        figsize=(10,12),
        verbose=False,
    ):
    solvers = ['WalkSAT', 'ProbSAT']

    xlims = dict(
        WalkSAT=[0,1],
        ProbSAT=[0,4],
    )
    ylims = dict(
        tms_entropy=[0, 1],
    )
    opt_value = dict(
        WalkSAT=(r'$\rho$', 0.4),
        ProbSAT=(r'$c_b$', 2.6),
    )
    metric_label = dict(
        tms_entropy=r'\overline{H\!\parens{M_F}}',
    )
    # load data

    all_data = load_noise_to_tms_entropy(
        in_filepath,
        solvers,
        only_convergent=True,
        verbose=verbose
    )

    # plot data
    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')
    fig, axes = pyplt.subplots(
        1,
        len(solvers),
        figsize=figsize
    )
    fig.tight_layout()
    for y, solver in enumerate(solvers):
        data = all_data[solver]
        # Scatterplot, if x1 == x2
        ax = axes[y]
        ax.set_xlim(xlims[solver])
        ax.set_ylim(ylims['tms_entropy'])
        seaborn.scatterplot(
            x='noise_param',
            y='tms_entropy',
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
        opt_mean = numpy.mean(data[at_opt_mean]['tms_entropy'])
        ax.axhline(
            y=opt_mean,
            label=f'${metric_label["tms_entropy"]} = {opt_mean:.3f}$',
            color='r',
            linestyle=':'
        )
        # Average lineplot in any case
        seaborn.lineplot(
            x='noise_param',
            y='tms_entropy',
            data=data,
            estimator=numpy.mean,
            ax=ax,
           # label='Mittelwert',
            color='g'
        )
        ax.set_xlabel(opt_value[solver][0])
        if solver == 'WalkSAT':
            ax.set_ylabel(f'${metric_label["tms_entropy"]}$')
        else:
            ax.set_ylabel('')
            ax.yaxis.set_major_formatter(pyplt.NullFormatter())

    seaborn.despine()
    fig.savefig(outfile, bbox_inches='tight')
