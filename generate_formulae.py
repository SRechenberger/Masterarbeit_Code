import sys
import os
from src.solver.utils import Formula

def usage():
    print('Usage: python generate_formulae.py [--usage | DIR NUM NUM_VARS RATIO [--seed SEED] [--poolsize POOLSIZE]] [--verbose]')
    print('  DIR        str     target directory')
    print('  NUM        int     number of formulae to generate')
    print('  NUM_VARS   int     number of variables of each formula')
    print('  RATIO      float   ratio #clauses/#variables')
    print('  SEED       int     random seed; default = current time')
    print('  POOLSIZE   int     number of processes to generate; default = 1')
    print('  --usage    prints this help message')
    print('  --verbose  prints written filenames')
    print('')
    print('Using with flag -O recommended')

def die(msg, system_error = False):
    if not system_error:
        print('User error: {}'.format(msg))
        usage()
    else:
        print('System error: {}'.format(msg))

    sys.exit(1)

if __name__ == '__main__':

    if sys.argv[1] == '--usage':
        usage()
        sys.exit(0)

    dir = None
    num = None
    num_vars = None
    ratio = None

    # default values
    seed = None
    pool_size = 1
    verbose = False

    flags = sys.argv[1:]
    flag_idx = 0
    while flag_idx < len(flags):
        flag = flags[flag_idx]
        if flag_idx == 0:
            dir = flag

        elif flag_idx == 1:
            try:
                num = int(flag)

            except ValueError:
                die('NUM argument is not an integer')

            if num <= 0:
                die('NUM must be greater than 0')

        elif flag_idx == 2:
            try:
                num_vars = int(flag)

            except ValueError:
                die('NUM_VARS argument is not an integer')

            if num_vars <= 0:
                die('NUM_VARS must be greater than 0')

        elif flag_idx == 3:
            try:
                ratio = float(flag)

            except ValueError:
                die('RATIO argument is not a float')

            if ratio <= 0:
                die('RATIO must be greater than 0')

        else:
            if flag == '--seed':
                try:
                    seed = int(flags[flag_idx+1])
                    flag_idx+=1

                except ValueError:
                    die('SEED is not an integer')

            elif flag == '--poolsize':
                try:
                    poolsize = int(flags[flag_idx+1])
                    flag_idx += 1

                except ValueError:
                    die('POOLSIZE is not an integer')

                if poolsize <= 0:
                    die('POOLSIZE must be greater than 0')

            elif flag == '--verbose':
                verbose = True

            else:
                die('What is this shit? {}'.format(flag))

        flag_idx += 1

    try:
        Formula.generate_formula_pool(
            dir,
            num,
            num_vars,
            ratio,
            seed=seed,
            poolsize=poolsize,
            verbose=verbose
        )
    except Exception as e:
        die(
            '{}'.format(str(e)),
            system_error = True
        )
