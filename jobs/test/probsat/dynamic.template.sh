#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=1:00:00
#MSUB -l pmem=3000mb
#MSUB -N probsat-dynamic-test
#MSUB -o /work/ul/ul_student/ul_pwn14/output/probsat_dynamic_test
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

N=$1
X=$2

module load devel/python/3.5.2

python -O run_experiment.py $WORK/input/n`echo $N` $X \
  --dynamic $((N/2)) $(($N*5)) \
  --probsat_poly 2.3 \
  --poolsize 16 \
  --database_file $WORK/output/experiments.db \
  --verbose
