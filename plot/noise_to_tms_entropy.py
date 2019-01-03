import seaborn
import numpy
import math

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, load_noise_to_tms_entropy, LABELS, OPT_VALUE

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
        converged=[0,1],
    )
    # load data

    all_data = load_noise_to_tms_entropy(
        in_filepath,
        solvers,
        only_convergent=False,
        verbose=verbose
    )

    # plot data
    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')
    fig, axes = pyplt.subplots(
        2,
        len(solvers),
        figsize=figsize
    )
    fig.tight_layout()
    for y, solver in enumerate(solvers):
        data = all_data[solver]
        # Scatterplot, if x1 == x2
        ax = axes[0][y]
        ax.set_xlim(xlims[solver])
        ax.set_ylim(ylims['tms_entropy'])
        seaborn.scatterplot(
            x='noise_param',
            y='tms_entropy',
            data=data[data['converged'] == 1],
            marker='+',
            ax=ax,
            alpha=0.8,
        )
        ax.axvline(
            x=OPT_VALUE[solver],
           # label=opt_value[solver][0],
            color='g',
            linestyle=':'
        )
        at_opt_mean = data['noise_param'] == OPT_VALUE[solver]
        opt_mean = numpy.mean(data[at_opt_mean]['tms_entropy'])
        ax.axhline(
            y=opt_mean,
            label=f'${LABELS["tms_entropy"]} = {opt_mean:.3f}$',
            color='r',
            linestyle=':'
        )
        # Average lineplot in any case
        data_tmp = data[data['converged'] == 1]
        seaborn.lineplot(
            x='noise_param',
            y='tms_entropy',
            data=data_tmp,
            estimator=numpy.mean,
            ax=ax,
           # label='Mittelwert',
            color='g'
        )
        seaborn.lineplot(
            x='noise_param',
            y='tms_entropy',
            data=data_tmp[data['tms_entropy'].between(0.1,0.9)],
            estimator=numpy.mean,
            ax=ax,
           # label='Mittelwert',
            linestyle=':',
            color='y'
        )
        ax.set_xlabel(f'${LABELS[solver]}$')
        if solver == 'WalkSAT':
            ax.set_ylabel(f'${LABELS["tms_entropy"]}$')
        else:
            ax.set_ylabel('')
            ax.yaxis.set_major_formatter(pyplt.NullFormatter())


        ax = axes[1][y]
        ax.set_xlim(xlims[solver])
        ax.set_ylim(ylims['converged'])
        conv_data = data.groupby('noise_param', as_index=False)['converged'].mean()
        seaborn.scatterplot(
            x='noise_param',
            y='converged',
            data=conv_data,
            ax=ax,
        )
        ax.set_xlabel(f'${LABELS[solver]}$')
        if solver == 'WalkSAT':
            ax.set_ylabel(f'${LABELS["conv"]}$')
        else:
            ax.set_ylabel('')
            ax.yaxis.set_major_formatter(pyplt.NullFormatter())




    seaborn.despine()
    fig.savefig(outfile, bbox_inches='tight')
