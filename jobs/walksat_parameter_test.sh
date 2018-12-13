#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l pmem=3000mb
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python -O run_experiment.py \
  $WORK/input/n512 \
  --dynamic $1 $2 \
  --walksat 0.57 \
  --poolsize 16 \
  --database_file $WORK/output/$3 \
  --repeat 10 \
  --verbose
