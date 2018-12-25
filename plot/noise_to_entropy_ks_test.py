import seaborn
import numpy
import math
import scipy
import pandas

import matplotlib.pyplot as pyplt

from plot.utils import PREAMBLE, DEFAULT_OUTFILE, load_dynamic_data

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=PREAMBLE
)


def plot_noise_to_entropy_ks_test(in_filepath, metric, outfile=DEFAULT_OUTFILE, field='average', verbose=False):
    solvers = ['WalkSAT', 'ProbSAT']
    xlims = dict(
        WalkSAT=[0,1],
        ProbSAT=[0,4],
    )
    opt_value = dict(
        WalkSAT=(r'\rho', 0.4),
        ProbSAT=(r'c_b', 2.4),
    )
    metric_label = dict(
        single_entropy=r'$H_1$',
        joint_entropy=r'$H_2$',
        mutual_information=r'$I$',
    )
    # load data

    all_data = load_dynamic_data(
        in_filepath,
        field,
        solvers,
        [metric],
        verbose=verbose
    )

    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')

    fig, axes = pyplt.subplots(1, 2, sharey=True, figsize=(12,6))
    for y, solver in enumerate(solvers):
        ax = axes[y]

        data = all_data[solver, metric]

        data = data.groupby('noise_param', as_index=False).agg(
            lambda df: scipy.stats.kstest(
                df['avg_value'],
                'skewnorm',
                scipy.stats.skewnorm.fit(df['avg_value']),
            )[0]
        )

        seaborn.scatterplot(
            x='noise_param',
            y='avg_value',
            data=data,
            ax=ax,
            legend='full',
        )

        opt_d = data[data['noise_param'] == opt_value[solver][1]]['avg_value'].iloc[0]
        print(opt_d)

        ax.axvline(
            x=opt_value[solver][1],
            label=f'${opt_value[solver][0]} = {opt_value[solver][1]}$ ' + r'$D_\alpha = {:.2f}$'.format(opt_d),
            color='#aaaaaa',
            linestyle=':',
        )
        for color, alpha in zip(['b','g','r','y'], [0.01, 0.05, 0.1, 0.2]):
            D = math.sqrt(-0.5*math.log(alpha/2)/100)

            ax.axhline(
                y=D,
                label=r'$\alpha = {:.2f}$ $D_\alpha \leq {:.2f}$'.format(alpha, D),
                color=color,
                linestyle='-.',
                alpha=0.5,
            )

        ax.set_xlabel(f'${opt_value[solver][0]}$')
        ax.set_ylabel(r'$D_\alpha$')
        ax.legend(loc='upper left')

    seaborn.despine()

    fig.savefig(outfile)
