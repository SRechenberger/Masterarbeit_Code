## Build status
[![Build Status](https://travis-ci.org/SRechenberger/sls_entropy.svg?branch=master)](https://travis-ci.org/SRechenberger/sls_entropy)

## Project Structure

### src
Contains all source code

#### src.utils
Contains utilities (may be obsolete).

#### src.solver
Contains all Algorithms including utilities.

##### src.solver.generic_solver
Contains the generic algorithm.

##### src.solver.gsat
Contains the GSAT algorithm as described in ([Selman et al. 1992](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.34.6853&rep=rep1&type=pdf))

##### src.solver.walksat
Contains the WalkSAT algorithm as described in ([Selman et al. 1994](http://www.aaai.org/Papers/AAAI/1994/AAAI94-051.pdf))

##### (Maybe TODO) src.solver.walksat_def
Alternative WalkSAT algorithm as described in ([Knuth 2015](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=13&ved=2ahUKEwiOu9PI-8HeAhVtwYsKHSvHAGgQFjAMegQICRAC&url=http%3A%2F%2Fptgmedia.pearsoncmg.com%2Fimages%2F9780134397603%2Fsamplepages%2F9780134397603.pdf&usg=AOvVaw3Vix2A9ieEBdfgyPsNcojt))

##### src.solver.probsat
Contains the GSAT algorithm as described in ([Balint & Schöning 2012](https://link.springer.com/chapter/10.1007/978-3-642-31612-8_3))

##### src.solver.utils
Contains utilities for Solvers (maybe move Assignment and Formula to a module src.sat).

#### src.experiment
Contains experimentation related stuff.

##### src.experiment.experiment
Contains Experiment class.

##### src.experiment.utils
Contains experimentation utilities.

## TODO (ordered by priority)
  1. minimum, maximum and average (?) *windowed* path entropy
     - minimum should be the most interesting (?)
     - all of them may be interesting, especially relative to d(a,a*)
  2. run some experiments
  3. more information in README.md
