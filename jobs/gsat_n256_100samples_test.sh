#!/bin/bash
#MSUB -l nodes=1:ppn16
#MSUB -l walltime=1:00:00
#MSUB -l pmem=3000mb
#MSUB -N gsat_n256_100samples_test
#MSUB -o $WORK/output/gsat_n256_100samples_test.txt
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python -O run_experiment.py $WORK/input/n256-r4.2 100 \
  --dynamic 100 $((256*5)) \
  --gsat \
  --poolsize 16 \
  --database_file $WORK/output/experiments.db \
  --verbose
