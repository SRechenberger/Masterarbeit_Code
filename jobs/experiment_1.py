import sys

from subprocess import call

PARAMS = dict(
    walksat = list(map(lambda x:x/10, range(0,11,1))),
    probsat = list(map(lambda x:x/10, range(0,42,2)))
)

MSUB = 'msub'

TEMPLATE = lambda static, jobflag, jobname, solver, param, infolder, outfolder, dbfolder: [
    MSUB,
    '-N', f'{solver}.{jobname}',
    '-o', f'{outfolder}',
    '-l', 'walltime={}'.format('5:00:00' if static else '4:00:00'),
    f'template.sh', f'\"--{solver} {param}\"',
    f'\"{jobflag}\"',
    f'{dbfolder}',
    f'{infolder}',
]

for solver in ['gsat','walksat','probsat']:
    if solver == 'gsat':
        call(
            TEMPLATE(
                False,
                '--dynamic',
                'dynamic_1',
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
                    f'dynamic_1_{p}',
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
                'static_1',
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
                    f'static_1_{p}',
                    solver,
                    f'{p}',
                    sys.argv[1],
                    sys.argv[2],
                    sys.argv[3],
                )
            )
