import math
import os
import src.analysis.dynamic_entropy as path_entropy


DEFAULT_OUTFILE = 'plot.pdf'

PREAMBLE = r"""
\usepackage{fourier}

\usepackage{amsthm}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{mathtools}
\usepackage{esvect}
\usepackage{nicefrac}
\usepackage{centernot}
\usepackage{dsfont}
\usepackage{bbm}
\numberwithin{equation}{subsection}

\newcommand{\negate}[1]{\bar{#1}}
\newcommand{\formulae}[0]{\mathcal{F}}
\newcommand{\knf}[0]{\mathrm{KNF}}
\newcommand{\kknf}[1]{#1\mathrm{KNF}}
\newcommand{\refsym}[2]{#1_{\mbox{\tiny{\ref{#2}}}}}
\newcommand{\var}[1]{\mathit{Var}\left(#1\right)}
\newcommand{\sat}[2]{\mathit{sat}\left(#1,#2\right)}
\newcommand{\unsat}[2]{\mathit{unsat}\left(#1,#2\right)}

\newcommand{\red}[1]{{\color{red}#1}}
\newcommand{\green}[1]{{\color{OliveGreen}#1}}

\newcommand{\name}[1]{\mathit{#1}}

\newcommand{\unif}[0]{\gets_{\Unif}}

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

% \newcommand{\vpair}[2]{\left(\begin{matrix}#1\\#2\end{matrix}\right)}
\newcommand{\vpair}[2]{\left(#1,#2\right)}
\newcommand*{\defeq}{\mathrel{\vcenter{\baselineskip0.5ex \lineskiplimit0pt
                     \hbox{\scriptsize.}\hbox{\scriptsize.}}}%
                     =}
"""

def load_dynamic_data(in_filepath, field, solvers, verbose=False):
    all_data = {}
    for solver in solvers:
        path = os.path.join(in_filepath, solver)
        all_data[solver] = path_entropy.noise_param_to_path_entropy(
            path,
            f'{field}',
            verbose=verbose,
        )

    return all_data
