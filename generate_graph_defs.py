import argparse
from src.formula import Formula, Assignment
from src.solver.utils import Falselist
from src.solver.gsat import gsat_distribution, GSATContext
from src.solver.walksat import walksat_distribution, DefensiveContext
from src.solver.probsat import probsat_distribution

parser = argparse.ArgumentParser()
grp = parser.add_mutually_exclusive_group(required=True)
grp.add_argument('--gsat', action='store_true')
grp.add_argument('--walksat', action='store_true')
grp.add_argument('--probsat', action='store_true')

args = parser.parse_args()

PATH = [1,2,1,3,1,2,1,0]

FORMULA = Formula(
    clauses=[[1, -2], [-1, 3], [2, 3], [1, 2]],
    num_vars=3,
    sat_assignment=Assignment(
        atoms=[True, True, True],
        num_vars=3,
    ),
)

ASSGNS = [0, 4, 6, 2, 3, 7, 5, 1]

def generate_probs(distribution, context):
    assgn = Assignment([False, False, False], 3)
    ctx = context(FORMULA, assgn)
    probs = []
    for i, a in zip(PATH, ASSGNS):
        probs.append((a, distribution(ctx)))
        if i > 0:
            ctx.update(i)

    return probs


def print_probs(probs):
    for state, line in probs:
        for i, prob in enumerate(line):
            state_2 = state if i == 0 else state ^ (1 << 3 - i)
            if prob > 0:
                print(f'{state}to{state_2} = {prob:.3f}')
            if prob == 1:
                print(f'{state}to{state_2} = 1')


if args.gsat:
    print_probs(generate_probs(gsat_distribution, GSATContext))
elif args.walksat:
    print_probs(generate_probs(walksat_distribution(0.57), DefensiveContext))
elif args.probsat:
    print_probs(generate_probs(probsat_distribution(4, 2.3), DefensiveContext))
