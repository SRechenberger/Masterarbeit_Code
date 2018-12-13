#!/bin/bash
#MSUB -l walltime=11:00:00
#MSUB -l nodes=1:ppn=16
#MSUB -l pmem=3000mb
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

RHO=$1

module load devel/python/3.5.2

python -O run_experiment.py \
  $WORK/input/n512 \
  --dynamic 600 10240 \
  --walksat $RHO \
  --poolsize 16 \
  --database_file $WORK/output/data/walksat-rho`echo $RHO`-dynamic.db \
  --repeat 10 \
  --verbose
