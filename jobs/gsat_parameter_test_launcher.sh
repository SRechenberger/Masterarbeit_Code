TRIES=2400
FLIPS=5*512

for i in {0..9}
do
  msub -l walltime=11:00:00 -N test_$((TRIES))_$((FLIPS))_$((i)) -o gsat_$((TRIES))_$((FLIPS))_$((i)).out jobs/gsat_parameter_test.sh $((TRIES)) $((FLIPS)) gsat_$((TRIES))_$((FLIPS))_$((i)).db
done
