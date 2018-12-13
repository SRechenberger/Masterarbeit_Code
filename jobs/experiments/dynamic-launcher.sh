# alias msub='echo msub'
# Run GSAT
msub \
  -o $WORK/output/stdout/gsat-dynamic.out \
  -N gsat-dynamic \
  jobs/experiments/gsat-dynamic.sh


# Run WalkSAT
for rho in $(cat jobs/experiments/walksat_params);
do
  msub \
    -o $WORK/output/stdout/walksat-`echo $rho`-dynamic.out \
    -N walksat-rho`echo $rho`-dynamic \
    jobs/experiments/walksat-dynamic.sh $rho
done

# Run ProbSAT
for cb in $(cat jobs/experiments/probsat_params);
do
  msub \
    -o $WORK/output/stdout/probsat-`echo $cb`-dynamic.out \
    -N probsat-cb`echo $cb`-dynamic \
    jobs/experiments/probsat-dynamic.sh $cb
done
