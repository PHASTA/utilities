#!/bin/bash
# Not tested in Script form. Maybe required to run from command line

## One line version for command line
# i=0; while [ -s batch1 ]; do i=$(($i+1)); rm Batch1-procs_case/*.*.*; mpirun -f $COBALT_NODEFILE -np 48 pvbatch BatchSync.py 1 1 2>&1 | tee -a output.Test1.$i; done

i=0
while [ -s batch1 ]
do i=$(($i+1))
    rm Batch1-procs_case/*.*.*
    mpirun -f $COBALT_NODEFILE -np 48 pvbatch BatchSync.py 1 1 2>&1 | tee -a output.Test1.$i
done
