import argparse
import time

from src.experiment.experiment import Experiment, StaticExperiment
from src.experiment.measurement import EntropyMeasurement

parser = argparse.ArgumentParser()

parser.add_argument(
    'input_dir',
    help='folder of input formulae',
    type=str,
)
parser.add_argument(
    'sample_size',
    help='number of formulae to draw',
    type=int,
)

experiment_type_group = parser.add_mutually_exclusive_group(required = True)
experiment_type_group.add_argument(
    '--dynamic',
    help='run dynamic experiment; needs max_flips and max_tries',
    nargs=2,
    type=int,
)

experiment_type_group.add_argument(
    '--static',
    help='run static experiment',
    action='store_true'
)

solver_group = parser.add_mutually_exclusive_group(required = True)
solver_group.add_argument(
    '--gsat',
    help = 'run with GSAT algorithm',
    action = 'store_true',
)
solver_group.add_argument(
    '--walksat',
    help = 'run with WalkSAT algorithm',
    nargs = 1,
    type = float,
)
solver_group.add_argument(
    '--probsat_poly',
    help = 'run with ProbSAT algorithm with polynomial phi function',
    nargs = 1,
    type = float,
)
solver_group.add_argument(
    '--probsat_exp',
    help = 'run with ProbSAT algorithm with exponential phi function',
    nargs = 1,
    type = float,
)

parser.add_argument(
    '--poolsize',
    help = 'number of parallel processes',
    type = int,
    default = 1,
)

parser.add_argument(
    '--database_file',
    help = 'database file for results',
    type = str,
    default = 'experiments.db',
)

parser.add_argument(
    '--repeat',
    help = 'number of experiments to run',
    type = int,
    default = 1,
)

parser.add_argument(
    '--verbose',
    help = 'measure and print time taken by each experiment',
    action = 'store_true',
)


def calc_time(seconds):
    s = seconds % 60
    m = (seconds // 60) % 60
    h = seconds // (60*60)
    return h, m, s


if __name__ == '__main__':
    args = parser.parse_args()

    if args.gsat:
        solver = 'gsat'
        setup = dict()
    elif args.walksat:
        solver = 'walksat'
        setup = dict(rho = args.walksat[0])
    elif args.probsat_poly:
        solver = 'probsat'
        setup = dict(
            c_break = args.probsat_poly[0],
            phi = 'poly'
        )
    elif args.probsat_exp:
        solver = 'probsat'
        setup = dict(
            c_break = args.probsat_poly[0],
            phi = 'exp'
        )

    count = 0
    while count < args.repeat:
        # setup
        if args.verbose:
            print('Experiment #{} setup... '.format(count+1), end = '', flush=True)

        if args.dynamic:
            e = Experiment(
                args.input_dir,
                args.sample_size,
                solver,
                args.dynamic[0],
                args.dynamic[1],
                EntropyMeasurement,
                poolsize=args.poolsize,
                database=args.database_file,
                **setup,
            )
        elif args.static:
            e = StaticExperiment(
                args.input_dir,
                args.sample_size,
                solver,
                poolsize=args.poolsize,
                database=args.database_file,
                **setup,
            )


        # running
        if args.verbose:
            print('running... ',end='', flush=True)
            begin_time = time.time()

        e.run_experiment()

        #saving
        if args.verbose:
            time_taken = time.time() - begin_time
            print(
                'finished in {}h {}m {}s...'.format(*calc_time(int(time_taken))),
                end = '',
                flush=True
            )
        e.save_results()
        if args.verbose:
            print('saved.', flush=True)
        count += 1

