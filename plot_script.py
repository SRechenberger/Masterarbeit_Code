# General Utilities
import argparse
import os
import multiprocessing

# Math stuff
import math
import numpy

# Plot stuff
import seaborn
import matplotlib.pyplot as pyplt

# Access Modules
import src.analysis.dynamic_entropy as path_entropy
import src.analysis.state_entropy as state_entropy
import src.analysis.tms_entropy as tms_entropy


from mpl_toolkits.axisartist.axislines import SubplotZero

A4_DIMS = (11.7, 8.27)
DEFAULT_OUTFILE = 'plot.pdf'

preamble=r"""
\usepackage{fourier}

\usepackage{amsthm}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{mathtools}
\usepackage{esvect}
\usepackage{nicefrac}
\usepackage{centernot}
\usepackage{dsfont}
\usepackage{bbm}
\numberwithin{equation}{subsection}

\newcommand{\negate}[1]{\bar{#1}}
\newcommand{\formulae}[0]{\mathcal{F}}
\newcommand{\knf}[0]{\mathrm{KNF}}
\newcommand{\kknf}[1]{#1\mathrm{KNF}}
\newcommand{\refsym}[2]{#1_{\mbox{\tiny{\ref{#2}}}}}
\newcommand{\var}[1]{\mathit{Var}\left(#1\right)}
\newcommand{\sat}[2]{\mathit{sat}\left(#1,#2\right)}
\newcommand{\unsat}[2]{\mathit{unsat}\left(#1,#2\right)}

\newcommand{\red}[1]{{\color{red}#1}}
\newcommand{\green}[1]{{\color{OliveGreen}#1}}

\newcommand{\name}[1]{\mathit{#1}}

\newcommand{\unif}[0]{\gets_{\Unif}}

\newcommand{\2}[0]{\frac{1}{2}}
\newcommand{\4}[0]{\frac{1}{4}}
\newcommand{\8}[0]{\frac{1}{8}}
\DeclareMathOperator*{\argmax}{arg\,max}
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\brk}{break}
\DeclareMathOperator*{\mk}{make}
\DeclareMathOperator*{\ind}{\mathds{1}}
\DeclareMathOperator*{\Prob}{P}
\DeclareMathOperator*{\Exp}{E}
\DeclareMathOperator*{\Unif}{uniform}
\DeclareMathOperator*{\Lang}{\mathcal{L}}
\DeclareRobustCommand{\bigO}{%
  \text{\usefont{OMS}{cmsy}{m}{n}O}%
}
\newcommand{\prob}[2][]{\Prob_{#1}\!\left[#2\right]}
\newcommand{\expect}[2][]{\Exp_{#1}\!\left[#2\right]}
\newcommand{\floor}[1]{\left\lfloor#1\right\rfloor}
\newcommand{\ceil}[1]{\left\lceil#1\right\rceil}
\newcommand{\parens}[1]{\left(#1\right)}
\newcommand{\set}[1]{\left\{#1\right\}}
\newcommand{\card}[1]{\left|#1\right|}
\newcommand{\lb}[0]{\log_2}
\newcommand{\etaf}[1]{#1 \cdot \lb #1}
\newcommand{\sonst}{\name{sonst}}
\newcommand{\equivp}[1]{\stackrel{#1}{\equiv}}
%\newcommand{\equivp}[1]{\stackrel{\equiv}{#1}}
\newcommand{\lang}[1]{\Lang\!\left[#1\right]}

% \newcommand{\vpair}[2]{\left(\begin{matrix}#1\\#2\end{matrix}\right)}
\newcommand{\vpair}[2]{\left(#1,#2\right)}
\newcommand*{\defeq}{\mathrel{\vcenter{\baselineskip0.5ex \lineskiplimit0pt
                     \hbox{\scriptsize.}\hbox{\scriptsize.}}}%
                     =}
"""

pyplt.rc('text', usetex=True)
pyplt.rc(
    'text.latex',
    preamble=preamble
)

FIX_NORM_FACTOR = dict(
    single_entropy = 1.125,
    joint_entropy = math.log(512,2)/math.log(255,2),
    mutual_information = math.log(512,2)/math.log(255,2),
)

def load_dynamic_data(in_filepath, field, solvers, metrics, verbose=False):
    all_data = {}
    for solver in solvers:
        path = os.path.join(in_filepath, solver)
        for metric in metrics:
            all_data[solver, metric] = path_entropy.noise_param_to_path_entropy(
                path, f'{metric}', f'{field}',
                verbose=verbose,
            )

    for key, data in all_data.items():
        all_data[key]['avg_value'] = data['avg_value'] * FIX_NORM_FACTOR[metric]

    return all_data


def plot_noise_to_performance(in_filepath, outfile=DEFAULT_OUTFILE, verbose=False):
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
        avg_runtime=r'$T_F$',
        avg_sat=r'$\prob{\mbox{„Erfolg“}}$',
    )
    seaborn.set()
    seaborn.set_style('ticks', {'axes.grid': True, 'grid.linestyle': '-'})
    seaborn.set_context('paper')
    fig, ((ax11,ax12),(ax21,ax22)) = pyplt.subplots(2, 2, figsize=A4_DIMS)
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
                marker='+',
                ax=ax,
                estimator=numpy.mean,
            )
            ax.set_xlabel(opt_value[solver][0])
            ax.set_ylabel(metric_label[metric])

    seaborn.despine()
    fig.savefig(outfile)


def plot_noise_entropy_overview(in_filepath, metric, outfile=DEFAULT_OUTFILE, field='average', verbose=False):
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
    fig, axes = pyplt.subplots(1, 2, sharey=True, figsize=A4_DIMS)
    for y, solver in enumerate(solvers):

        # Scatterplot, if x1 == x2
        ax = axes[y]
        ax.set_xlim(xlims[solver])
        data = all_data[solver, metric]
        seaborn.scatterplot(
            x='noise_param',
            y='avg_value',
            data=data,
            marker='+',
            ax=ax,
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
    fig, axes = pyplt.subplots(1, 3, sharex=True, sharey=True, figsize=A4_DIMS)
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

    fig.savefig(outfile)



argparser = argparse.ArgumentParser(description='Plot figures')

argparser.add_argument(
    'data_folder',
    type=str,
    help='data input root folder'
)

argparser.add_argument(
    '--outfile',
    type=str,
    help='output file; default: plot.pdf'
)

argparser.add_argument(
    '--verbose',
    action='store_true',
    help='verbose output'
)

argparser.add_argument(
    '--noise_to_entropy_overview',
    type=str,
    nargs=2,
    metavar=('METRIC','FIELD'),
    help='Plots figure to compare noise parameter and entropy for a specific field FIELD'
)

argparser.add_argument(
    '--path_entropy_to_performance',
    type=str,
    nargs=2,
    metavar=('METRIC','FIELD'),
    help='Plots figure to compare entropy and performance'
)


argparser.add_argument(
    '--noise_to_performance',
    action='store_true',
    help='Plot Performance as function of noise-param. for WalkSAT and ProbSAT'
)

args = argparser.parse_args()

if __name__ == '__main__':
    infolder = args.data_folder
    if args.outfile:
        outfile = args.outfile
    else:
        outfile = DEFAULT_OUTFILE

    if args.noise_to_performance:
        plot_noise_to_performance(
            args.data_folder,
            outfile=outfile,
            verbose=args.verbose,
        )

    if args.noise_to_entropy_overview:
        plot_noise_entropy_overview(
            args.data_folder,
            args.noise_to_entropy_overview[0],
            outfile=outfile,
            field=args.noise_to_entropy_overview[1],
            verbose=args.verbose,
        )
        if args.verbose:
            print('Done.')

    if args.path_entropy_to_performance:
        plot_path_entropy_to_performance(
            args.data_folder,
            args.path_entropy_to_performance[0],
            outfile=outfile,
            field=args.path_entropy_to_performance[1],
            verbose=args.verbose,
        )
        if args.verbose:
            print('Done.')








