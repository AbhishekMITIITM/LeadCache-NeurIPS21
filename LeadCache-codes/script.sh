#!/bin/bash
#PBS -e errorfile.err
#PBS -o logfile.log
#PBS -l select=1:ncpus=4
#PBS -l walltime=140:00:00
#PBS -M abhishek.sinha@ee.iitm.ac.in
#PBS -N ICML21 
tpdir=`echo $PBS_JOBID | cut -f 1 -d .`
tempdir=$HOME/scratch/job$tpdir
mkdir -p $tempdir
cd $tempdir
cp -R $PBS_O_WORKDIR/* .
module load anaconda3_2020
python driver2.py
#python popularity.py
#./a.out >output.txt
#rm a.out
mv ../job$tpdir $PBS_O_WORKDIR/.
