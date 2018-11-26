#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=1:00:00
#MSUB -l pmem=3000mb
#MSUB -N gsat-dynamic-n256-300-test
#MSUB -o /work/ul/ul_student/ul_pwn14/output/gsat_n256_100samples_test.txt
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python -O run_experiment.py $WORK/input/n256-r4.2 300 \
  --dynamic 100 $((256*5)) \
  --gsat \
  --poolsize 16 \
  --database_file $WORK/output/experiments.db \
  --verbose
