#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=5:00:00
#MSUB -l pmem=3000mb
#MSUB -N walksat-dynamic
#MSUB -o /work/ul/ul_student/ul_pwn14/output/walksat_dynamic
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

RHO=$1

module load devel/python/3.5.2

python -O run_experiment.py $WORK/input/n512 \
  --dynamic 100 20000 \
  --walksat $RHO \
  --poolsize 16 \
  --database_file $WORK/output/walksat`echo $RHO`.dynamic.db \
  --repeat 10
