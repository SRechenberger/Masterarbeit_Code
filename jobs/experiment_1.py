import sys

from subprocess import call

PARAMS = dict(
    walksat = list(map(lambda x:float(x)/10, range(0,11,1))),
    probsat = list(map(lambda x:float(x)/10, range(0,42,2)))
)

MSUB = 'echo'

NAME = lambda static, solver, param: '{}.{}.{}'.format(
    'static' if static else 'dynamic',
    solver,
    0 if solver == 'gsat' else param
)

TEMPLATE = lambda static, jobflag, solver, param, infolder, outfolder, dbfolder, repeat: [
    MSUB,
    '-N', NAME(static, solver, param),
    '-o', outfolder + '/' + NAME(static, solver, param) + '.out',
    '-l', 'walltime={}'.format('5:00:00' if static else '4:00:00'),
    'jobs/template.sh', '"--{} {}"'.format(solver, param),
    '"{}"'.format(jobflag),
    dbfolder + '/' + NAME(static, solver, param) + '.db',
    infolder,
    str(repeat),
]

if sys.argv[1] == 'dynamic':
    for solver in ['gsat','walksat','probsat']:
        if solver == 'gsat':
            call(
                TEMPLATE(
                    False,
                    '--dynamic 100 20000',
                    solver,
                    '',
                    sys.argv[2],
                    sys.argv[3],
                    sys.argv[4],
                    10,
                )
            )
        else:
            for p in PARAMS[solver]:
                call(
                    TEMPLATE(
                        False,
                        '--dynamic 100 20000',
                        solver,
                        str(p),
                        sys.argv[2],
                        sys.argv[3],
                        sys.argv[4],
                        10,
                    )
                )

elif sys.argv[1] == 'static':
    for solver in ['gsat','walksat','probsat']:
        if solver == 'gsat':
            call(
                TEMPLATE(
                    True,
                    '--static',
                    solver,
                    '',
                    sys.argv[2],
                    sys.argv[3],
                    sys.argv[4],
                    1,
                )
            )
        else:
            for p in PARAMS[solver]:
                call(
                    TEMPLATE(
                        True,
                        '--static',
                        solver,
                        str(p),
                        sys.argv[2],
                        sys.argv[3],
                        sys.argv[4],
                        1,
                    )
                )
