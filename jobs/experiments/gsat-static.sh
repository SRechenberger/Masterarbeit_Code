#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=8:00:00
#MSUB -l pmem=3000mb
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode


module load devel/python/3.5.2

python -O run_experiment.py $WORK/input/n512 \
  --static \
  --gsat \
  --poolsize 16 \
  --database_file $WORK/output/data/gsat-0.db \
  --verbose
