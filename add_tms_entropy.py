import argparse
import os
import time
import sys
import sqlite3

from src.analysis.tms_entropy import add_tms_entropy

argparser = argparse.ArgumentParser(
    description='Calculate and add TMS-Entropy to database file; BACKUP YOUR FILES'
)

argparser.add_argument(
    'folders',
    type=str,
    nargs='+',
    help='folders of database files',
)

argparser.add_argument(
    '--max_loops',
    type=int,
    default=10000,
    help='maximum number of iterations for approximating the stationary distribution',
)

argparser.add_argument(
    '--eps_exp',
    type=int,
    default=15,
    help='exponent for setting the tolerance for the approximation; eps = 2 ** -eps_exp',
)

argparser.add_argument(
    '--noupdate',
    action='store_false',
    help='if set, already saved TMS-entropy in the database will not be overwritten',
)

argparser.add_argument(
    '--poolsize',
    type=int,
    default=1,
    help='number of parallel processes',
)

argparser.add_argument(
    '--verbose',
    action='store_true',
    help='more output',
)

ARGS = argparser.parse_args()

def time_tuple(time):
    secs = round(time)
    mins = secs // 60
    secs %= 60
    hours = mins // 60
    mins %= 60
    return hours, mins, secs

if __name__ == '__main__':
    if ARGS.verbose:
        print(f'collecting files from {len(ARGS.folders)} folders... ', end='', flush=True)

    files = []
    for folder in ARGS.folders:
        for file in os.listdir(folder):
            if file.endswith('.db'):
                files.append(os.path.join(folder, file))

    if ARGS.verbose:
        print(f'{len(files)} collected.')

    for i, file in enumerate(files):
        if ARGS.verbose:
            print(f'file {i+1}/{len(files)}: {file}... ', end='', flush=True)
            print('begin... ', end='', flush=True)
            t_begin = time.time()

        try:
            add_tms_entropy(
                file,
                eps_exp=ARGS.eps_exp,
                max_loops=ARGS.max_loops,
                update=ARGS.noupdate,
                poolsize=ARGS.poolsize,
            )

        except sqlite3.OperationalError as e:
            print(f'skipped file {file} because of {type(e).__name__}: {e}')
            continue

        except Exception as e:
            print(f'stopped at file {file} because of {type(e).__name__}: {e}.')
            sys.exit(1)

        if ARGS.verbose:
            t_end = time.time()
            hours, mins, secs = time_tuple(t_end-t_begin)
            print(f'end {hours:02d}:{mins:02d}:{secs:02d}.')
        else:
            print('.', end='', flush=True)

    if ARGS.verbose:
        print('done.')

