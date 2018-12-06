NAME=static_experiment_1

# GSAT
sh ../gsat.static.template.sh 256 $NAME

# WalkSAT
for i in $(cat walksat_parameters);
do
  sh ../walksat.static.template.sh 256 $i $NAME;
done;

# ProbSAT
for i in $(cat probsat_parameters);
do
  sh ../probsat.static.template.sh 256 $i $NAME;
done;

