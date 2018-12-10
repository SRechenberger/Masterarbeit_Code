#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=5:00:00
#MSUB -l pmem=3000mb
#MSUB -N gsat-static
#MSUB -o /work/ul/ul_student/ul_pwn14/output/gsat_static
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode


module load devel/python/3.5.2

python -O run_experiment.py $4 \
  $2 \
  $1 \
  --poolsize 16 \
  --database_file $3 \
  --verbose \
  --repeat $5
