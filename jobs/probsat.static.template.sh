#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=3:00:00
#MSUB -l pmem=3000mb
#MSUB -N probsat-static
#MSUB -o /work/ul/ul_student/ul_pwn14/output/probsat_static
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

N=$1
CBR=$2
NAME=$3

module load devel/python/3.5.2

python -O run_experiment.py $WORK/input/n`echo $N` \
  --static 10 100 $((20*N)) \
  --probsat $CBR \
  --poolsize 16 \
  --database_file $WORK/output/`echo $NAME`.probsat.db \
