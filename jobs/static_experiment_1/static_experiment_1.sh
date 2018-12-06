NAME=static_experiment_1
WALKSAT="0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0"
PROBSAT="0.0 0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0 2.2 2.4 2.6 2.8 3.0 3.2 3.4 3.6 3.8 4.0"

# GSAT
msub jobs/gsat.static.template.sh 256 $NAME

# WalkSAT
for i in $WALKSAT;
do
  msub jobs/walksat.static.template.sh 256 $i $((NAME))_rho$i;
done;

# ProbSAT
for i in $PROBSAT;
do
  msub jobs/probsat.static.template.sh 256 $i $((NAME))_cb$i;
done;

