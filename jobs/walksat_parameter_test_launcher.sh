TRIES=600
FLIPS=20*512

for i in {0..9}
do
  msub -l walltime=11:00:00 -N walksat_$((TRIES))_$((FLIPS))_$((i)) -o $WORK/output/walksat_$((TRIES))_$((FLIPS))_$((i)).out jobs/walksat_parameter_test.sh $((TRIES)) $((FLIPS)) walksat_$((TRIES))_$((FLIPS))_$((i)).db
done
