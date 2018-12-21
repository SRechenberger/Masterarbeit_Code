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

A4_DIMS = (11.7, 8.27)
DEFAULT_OUTFILE = 'plot.pdf'

def load_dynamic_data(in_filepath, field, solvers, metrics, verbose=False):
    all_data={}
    #with multiprocessing.Pool(processes=3) as pool:
    for solver in solvers:
        path = os.path.join(in_filepath, solver)
        for metric in metrics:
            if verbose:
                print(f"Sparking load of {metric} {field} from {path}.")

            all_data[solver, metric] = path_entropy.noise_param_to_path_entropy(
                *(path, f'{metric}', f'{field}'),
                **dict(verbose=verbose),
            )

  #  for (solver, metric), fut_val in all_data.items():
  #      if verbose:
  #          print(f"Waiting for {metric} {field} from {solver}.")

  #      all_data[solver, metric] = fut_val.get()


    return all_data



def plot_noise_entropy_overview(in_filepath, outfile=DEFAULT_OUTFILE, field='average', verbose=False):
    solvers = ['WalkSAT', 'ProbSAT']
    metrics = ['single_entropy', 'joint_entropy', 'mutual_information']
    # load data

    all_data = load_dynamic_data(in_filepath, field, solvers, metrics, verbose=verbose)

    # plot data
    fig, axes = pyplt.subplots(3, 2, sharex=True, sharey=True, figsize=A4_DIMS)
    for y, solver in enumerate(solvers):
        for x1, metric in enumerate(metrics):
            for x2, _ in enumerate(metrics):
                if verbose:
                    print(f"Plotting {'scatterplot' if x1 == x2 else 'lineplot'} of {metrix} for {solver}")

                # Scatterplot, if x1 == x2
                ax = axs[y][x2]
                data = all_data[solver, metric]
                if x1 == x2:
                    seaborn.scatterplot(
                        x='noise_param',
                        y='avg_value',
                        data=data,
                        marker='o',
                        ax=ax,
                    )
                # Average lineplot, if x1 != x2
                else:
                    seaborn.lineplot(
                        x='noise_param',
                        y='avg_value',
                        data=data,
                        estimator=numpy.mean,
                        ax=ax,
                    )

    fig.savefig(outfile)



def path_entropy_to_performance(in_filepath, outfile=DEFAULT_OUTFILE, field='average', verbose=False):
    solvers = ['GSAT', 'WalkSAT', 'ProbSAT']
    metrics = ['single_entropy', 'joint_entropy', 'mutual_information']

    # load data
    all_data = load_dynamic_data(in_filepath, field, solvers, metrics, verbose=verbose)

    fig, axes = pyplt.subplots(3, 3, sharex=True, sharey=True, figsize=A4_DIMS)
    for y, solver in enumerate(solver_folders):
        for x1, metric in enumerate(metrics):
            for x2, _ in enumerate(metrics):
                if verbose:
                    print(f"Plotting {'scatterplot' if x1 == x2 else 'lineplot'} of {metrix} for {solver}")

                # Scatterplot, if x1 == x2
                ax = axs[y][x2]
                data = all_data[solver, metric]
                if x1 == x2:
                    seaborn.scatterplot(
                        x='noise_param',
                        y='avg_value',
                        data=data,
                        marker='o',
                        ax=ax,
                    )
                # Average lineplot, if x1 != x2
                else:
                    seaborn.lineplot(
                        x='noise_param',
                        y='avg_value',
                        data=data,
                        estimator=numpy.mean,
                        ax=ax,
                    )

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
    nargs=1,
    metavar='FIELD',
    help='Plots figure to compare noise parameter and entropy for a specific field FIELD'
)

args = argparser.parse_args()

if __name__ == '__main__':
    if args.noise_to_entropy_overview:
        plot_noise_entropy_overview('/media/sf_VBoxshare/MasterarbeitDaten', verbose=args.verbose)
        if args.verbose:
            print('Done.')

    else:
        if args.verbose:
            print('Nothing to do.')








