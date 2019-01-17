import math
import os
import src.analysis.dynamic_entropy as path_entropy
import src.analysis.tms_entropy as tms_entropy


DEFAULT_OUTFILE = 'plot.pdf'

PREAMBLE = r"""
\usepackage{amsthm}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{mathtools}
\usepackage{esvect}
\usepackage{nicefrac}
\usepackage{centernot}
\usepackage{dsfont}
\usepackage{bbm}
\numberwithin{equation}{subsection}

\usepackage{fourier}
\usepackage{fouriernc}


\newcommand{\2}[0]{\frac{1}{2}}
\newcommand{\4}[0]{\frac{1}{4}}
\newcommand{\8}[0]{\frac{1}{8}}
\DeclareMathOperator*{\argmax}{arg\,max}
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\brk}{break}
\DeclareMathOperator*{\mk}{make}
\DeclareMathOperator*{\ind}{\mathds{1}}
\DeclareMathOperator*{\Prob}{P}
\DeclareMathOperator*{\Exp}{E}
\DeclareMathOperator*{\Unif}{uniform}
\DeclareMathOperator*{\Lang}{\mathcal{L}}
\DeclareMathOperator*{\Unsat}{unsat}
\DeclareMathOperator*{\Sat}{sat}
\DeclareRobustCommand{\bigO}{%
  \text{\usefont{OMS}{cmsy}{m}{n}O}%
}
\newcommand{\prob}[2][]{\Prob_{#1}\!\left[#2\right]}
\newcommand{\expect}[2][]{\Exp_{#1}\!\left[#2\right]}
\newcommand{\floor}[1]{\left\lfloor#1\right\rfloor}
\newcommand{\ceil}[1]{\left\lceil#1\right\rceil}
\newcommand{\parens}[1]{\left(#1\right)}
\newcommand{\set}[1]{\left\{#1\right\}}
\newcommand{\card}[1]{\left|#1\right|}
\newcommand{\lb}[0]{\log_2}
\newcommand{\etaf}[1]{#1 \cdot \lb #1}
\newcommand{\sonst}{\name{sonst}}
\newcommand{\equivp}[1]{\stackrel{#1}{\equiv}}
%\newcommand{\equivp}[1]{\stackrel{\equiv}{#1}}
\newcommand{\lang}[1]{\Lang\!\left[#1\right]}
\newcommand{\negate}[1]{\bar{#1}}
\newcommand{\formulae}[0]{\mathcal{F}}
\newcommand{\knf}[0]{\mathrm{KNF}}
\newcommand{\kknf}[1]{#1\mathrm{KNF}}
\newcommand{\refsym}[2]{#1_{\mbox{\tiny{\ref{#2}}}}}
\newcommand{\var}[1]{\mathit{Var}\!\left(#1\right)}
\newcommand{\sat}[2]{\Sat_{#1}\!\parens{#2}}
\newcommand{\unsat}[2]{\Unsat_{#1}\!\parens{#2}}

\newcommand{\red}[1]{{\color{red}#1}}
\newcommand{\green}[1]{{\color{OliveGreen}#1}}

\newcommand{\name}[1]{\mathit{#1}}

\newcommand{\unif}[0]{\gets_{\Unif}}

% \newcommand{\vpair}[2]{\left(\begin{matrix}#1\\#2\end{matrix}\right)}
\newcommand{\vpair}[2]{\left(#1,#2\right)}
\newcommand*{\defeq}{\mathrel{\vcenter{\baselineskip0.5ex \lineskiplimit0pt
                     \hbox{\scriptsize.}\hbox{\scriptsize.}}}%
                     =}
"""


LABELS = dict(
    single_entropy=r'\overline{\hat H_1\!\parens{P}}',
    joint_entropy=r'\overline{\hat H_2\!\parens{P}}',
    cond_entropy=r'\overline{\hat H_S\!\parens{P}}',
    mutual_information=r'\overline{\hat I\!\parens{P}}',
    state_entropy=r'\overline{H\!\parens{Q_A | F, h}}',
    state_entropy_square=r'2^{\overline{H\!\parens{Q_A | F, h}}}',
    unsat=r'\overline{\card{\unsat{F}{A}}}',
    tms_entropy=r'\hat H\!\parens{M_F}',
    runtime=r'\overline{T_F}',
    ks_stat=r'D',
    WalkSAT=r'\rho',
    ProbSAT=r'c_b',
    conv=r'\kappa',
    hamming_dist=r'$\frac{d\!\parens{A_F^*, A}}{N_F}$',
)

OPT_VALUE = dict(
    WalkSAT=0.4,
    ProbSAT=2.4,
)

SOLVER_LABELS = dict(
    gsat='GSAT',
    walksat='WalkSAT',
    probsat='ProbSAT',
)

SOLVER_OPT_LABELS = dict(
    gsat='GSAT',
    walksat='WalkSAT_Opt',
    probsat='ProbSAT_Opt',
)



def load_from_all_subfolders(load_function, in_filepath, subfolders, *args, verbose=False, **kwargs):
    all_data = {}
    for subfolder in subfolders:
        path = os.path.join(in_filepath, subfolder)
        if verbose:
            print(f'Loading from {path}... ', end='', flush=True)

        try:
            all_data[subfolder] = load_function(path, *args, **kwargs)

        except Exception as e:
            print(f'Failed: {type(e).__name__} {e}.')
            raise e

        if verbose:
            print('Done.')

    return all_data

def load_dynamic_data(in_filepath, field, solvers, verbose=False):
    all_data = {}
    for solver in solvers:
        path = os.path.join(in_filepath, solver)
        all_data[solver] = path_entropy.noise_param_to_path_entropy(
            path,
            field,
            verbose=verbose,
        )

    return all_data

def load_runtime_to_entropy(in_filepath, field, solvers, mapping=None, verbose=False):
    all_data = {}
    for solver in solvers:
        if mapping:
            path = os.path.join(in_filepath, mapping[solver])
        else:
            path = os.path.join(in_filepath, solver)
        print(path)
        all_data[solver] = path_entropy.path_entropy_to_runtime(
            path,
            field,
            verbose=verbose,
        )

    return all_data

def load_noise_to_tms_entropy(in_filepath, solvers, only_convergent=True, verbose=False):
    all_data = {}
    for solver in solvers:
        path = os.path.join(in_filepath, solver)
        all_data[solver] = tms_entropy.tms_entropy_values(
            path,
            only_convergent=only_convergent,
            verbose=verbose,
        )

    return all_data
