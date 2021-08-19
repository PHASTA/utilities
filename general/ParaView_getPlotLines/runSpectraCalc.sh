#!/usr/bin/env bash

source /etc/profile.d/00softenv.sh
soft add @paraview-5.4.1

script=./SpectraLinePVTrace.py

mpirun -np $1 pvbatch $script
