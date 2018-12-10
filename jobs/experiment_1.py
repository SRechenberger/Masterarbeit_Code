import sys

from subprocess import call

PARAMS = dict(
    walksat = list(map(lambda x:x/10, range(0,11,1))),
    probsat = list(map(lambda x:x/10, range(0,42,2)))
)

MSUB = 'msub'

TEMPLATE = lambda static, jobflag, solver, param, infolder, outfolder, dbfolder: [
    MSUB,
    '-N', f'{"static" if static else "dynamic"}.{solver}.{0 if solver == "gsat" else param}',
    '-o', f'{outfolder}/{"static" if static else "dynamic"}.{solver}.{0 if solver == "gsat" else param}.out',
    '-l', 'walltime={}'.format('5:00:00' if static else '4:00:00'),
    f'template.sh', f'\"--{solver} {param}\"',
    f'\"{jobflag}\"',
    f'{dbfolder}/{"static" if static else "dynamic"}.{solver}.{0 if solver == "gsat" else param}.out',
    f'{infolder}',
]

for solver in ['gsat','walksat','probsat']:
    if solver == 'gsat':
        call(
            TEMPLATE(
                False,
                '--dynamic 100 20000',
                solver,
                '',
                sys.argv[1],
                sys.argv[2],
                sys.argv[3],
            )
        )
    else:
        for p in PARAMS[solver]:
            call(
                TEMPLATE(
                    False,
                    f'--dynamic 100 20000',
                    solver,
                    f'{p}',
                    sys.argv[1],
                    sys.argv[2],
                    sys.argv[3],
                )
            )


for solver in ['gsat','walksat','probsat']:
    if solver == 'gsat':
        call(
            TEMPLATE(
                True,
                '--static',
                solver,
                '',
                sys.argv[1],
                sys.argv[2],
                sys.argv[3],
            )
        )
    else:
        for p in PARAMS[solver]:
            call(
                TEMPLATE(
                    True,
                    f'--static',
                    solver,
                    f'{p}',
                    sys.argv[1],
                    sys.argv[2],
                    sys.argv[3],
                )
            )
