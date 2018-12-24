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


from plot.noise_to_entropy_overview import plot_noise_to_entropy_overview
from plot.noise_to_performance import plot_noise_to_performance
from plot.path_entropy_to_performance import plot_path_entropy_to_performance
from plot.noise_to_transferred_information import plot_noise_to_transferred_information

from mpl_toolkits.axisartist.axislines import SubplotZero

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

argparser.add_argument(
    '--noise_to_transferred_information',
    type=str,
    nargs=1,
    metavar='FIELD',
    help='Plots figure of transfered information ratio'
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
        plot_noise_to_entropy_overview(
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

    if args.noise_to_transferred_information:
        plot_noise_to_transferred_information(
            args.data_folder,
            outfile=outfile,
            field=args.noise_to_transferred_information[0],
            verbose=args.verbose,
        )
        if args.verbose:
            print('Done.')








