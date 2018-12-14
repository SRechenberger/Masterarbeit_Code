#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=17:00:00
#MSUB -l pmem=3000mb
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

RHO=$1

module load devel/python/3.5.2

python -O run_experiment.py $WORK/input/n512 \
  --static \
  --walksat $RHO \
  --poolsize 16 \
  --database_file $WORK/output/data/walksat-rho`echo $RHO`.db \
  --verbose
