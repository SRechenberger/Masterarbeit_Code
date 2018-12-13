# alias msub='echo msub'
# Run GSAT
msub \
  -o $WORK/output/stdout/gsat-static.out \
  -N gsat-static \
  jobs/experiments/gsat-static.sh


# Run WalkSAT
for rho in $(cat jobs/experiments/walksat_params);
do
  msub \
    -o $WORK/output/stdout/walksat-`echo $rho`-static.out \
    -N walksat-rho`echo $rho`-static \
    jobs/experiments/walksat-static.sh $rho
done

# Run ProbSAT
for cb in $(cat jobs/experiments/probsat_params);
do
  msub \
    -o $WORK/output/stdout/probsat-`echo $cb`-static.out \
    -N probsat-cb`echo $cb`-static \
    jobs/experiments/probsat-static.sh $cb
done
