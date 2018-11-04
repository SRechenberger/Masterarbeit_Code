import argparse

from src.experiment.experiment import Experiment
from src.experiment.utils import EntropyMeasurement

parser = argparse.ArgumentParser()

parser.add_argument(
    'input_dir',
    help = 'folder of input formulae',
    type = str,
)
parser.add_argument(
    'sample_size',
    help = 'number of formulae to draw',
    type = int,
)

parser.add_argument(
    'max_tries',
    help = 'maximum number of tries',
    type = int,
)
parser.add_argument(
    'max_flips',
    help = 'maximum number of flips per try',
    type = int,
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
    nargs = 2,
    type = float,
)
solver_group.add_argument(
    '--probsat_exp',
    help = 'run with ProbSAT algorithm with exponential phi function',
    nargs = 2,
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
            c_make = args.probsat_poly[0],
            c_break = args.probsat_poly[1],
            phi = 'poly'
        )


    count = 0
    while count < args.repeat:
        e = Experiment(
            args.input_dir,
            args.sample_size,
            solver,
            args.max_tries,
            args.max_flips,
            EntropyMeasurement,
            poolsize = args.poolsize,
            database = args.database_file,
            **setup,
        )
        e.run_experiment()
        e.save_results()
        count += 1

