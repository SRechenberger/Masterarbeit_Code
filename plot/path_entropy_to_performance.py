import seaborn
import numpy
import math

import matplotlib.pyplot as pyplt

from plot.utils import \
    PREAMBLE, DEFAULT_OUTFILE, load_runtime_to_entropy, LABELS, SOLVER_LABELS, SOLVER_OPT_LABELS

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)

def plot_path_entropy_to_performance(
        in_filepath,
        metrics,
        outfile=DEFAULT_OUTFILE,
        field='average',
        figsize=(10, 12),
        verbose=False,
    ):
    solvers = ['gsat', 'walksat', 'probsat']

    figsize = (
        figsize[0],
        figsize[1]/4 * len(metrics),
    )

    # load data
    all_data = load_runtime_to_entropy(
        in_filepath,
        field,
        solvers,
        mapping=SOLVER_OPT_LABELS,
        verbose=verbose,
    )

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
    titles_given = []
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
            h_mean = numpy.mean(data[metric])
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
            ax.set_xlabel(f'${LABELS[metric]}$')
            ax.set_ylabel(f'${LABELS["runtime"]}$')
            if solver not in titles_given:
                ax.set_title(f'\Large {SOLVER_LABELS[solver]}')
                titles_given.append(solver)

    seaborn.despine()

    fig.savefig(outfile, bbox_inches='tight')
