#!/usr/bin/env python3
import argparse
from math import ceil,floor

Description="""This utility will calculate the best arrangement of MPI Processors
and Nodes for a given number of partitions and node architecture. If the
architecture is specified, the appropriate PBS settings will be printed.

Examples:
\tnode_calc.py 1024 -o 3 -c 20
\tnode_calc.py 1024 -a sky_ele"""

## Parsing script input
class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """To display defaults in help and have a multiline help description"""
    # Shamelessly ripped from https://stackoverflow.com/a/18462760/7564988
    pass

parser = argparse.ArgumentParser(description=Description,
                                 formatter_class=CustomFormatter,
                                 prog='nodecalc')
parser.add_argument('parts', help='Number of partitions/MPI processes', type=int)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-a', '--architecture', help='The hardware architecture',
                    choices=['sky_ele', 'ivy', 'bro', 'has', 'san', 'N/A'], default='N/A')
group.add_argument('-c', '--cores', help='Cores per node',
                    type=int)
parser.add_argument('-o', '--oversubscribe', help='Threads/MPI Processes per core',
                    type=int, dest='threads', default=1)

args = parser.parse_args()


## Setting defaults for architectures
coresPerNode = {'bro':28, 'ivy':20, 'sky_ele':40, 'san':8, 'has':24,
                'N/A':args.cores}

## Calculating basic quantities to be used later
cores = coresPerNode[args.architecture] # Number of cores per node
mpiProcsTot = cores*args.threads # Number of MPI process per node

print('{:>30}: {}'.format('Cores per node', cores))
print('{:>30}: {}'.format('MPI Processes per core', args.threads))
print('{:>30}: {}'.format('MPI Processes per node', mpiProcsTot))
print('{:>30}: {} \n'.format('Total Desired MPI Processes', args.parts))

totalNodes = ceil(args.parts/mpiProcsTot)

# Following algorithm uses the following math expressions:
#    Assume the solution takes the following form:
#       nodes1*mpi1 + nodes2*mpi2 = parts (1)
#
#
#    with the following contraints:
#        nodes1 + nodes2 = totalNodes   (2)
#        mpi1 - mpi2 = 1                (3)
#
# Taking this system of equations, we get the following expression:
#    nodes1 = parts + totalNodes - totalNodes*mpi1
#
# Therefore we loop through the possible values of mpi1 in [mpiProcsTot,1]
#  until a realistic solution is found.

success=False
for mpi1 in range(mpiProcsTot, 1, -1):
    nodes1 = args.parts + totalNodes - totalNodes*mpi1
    if nodes1<=totalNodes and nodes1 > 0:
        success=True
        break

if not success:
    ValueError('An appropriate combination of resources was not found.')

mpi2 = mpi1 - 1
nodes2 = totalNodes - nodes1

print('{:>15}  {:^10} {:<20}'.format('','MPIProcs', 'Number of Nodes'))
print('{:>15}: {:^10} {:<20}'.format('First Chunk', mpi1, nodes1))
print('{:>15}: {:^10} {:<20} \n'.format('Second Chunk', mpi2, nodes2))

# Ensure that the result is correct
assert nodes1*mpi1 + nodes2*mpi2 == args.parts

resourcestring = '#PBS -l '
resourcestring += 'select={nodes}:ncpus={cores}:mpiprocs={mpiprocs}:model={model}'.format(
    nodes=nodes1, cores=min(cores,mpi1), mpiprocs=mpi1, model=args.architecture)
resourcestring += '+{nodes}:ncpus={cores}:mpiprocs={mpiprocs}:model={model}'.format(
    nodes=nodes2, cores=min(cores,mpi2), mpiprocs=mpi2, model=args.architecture)

print(resourcestring)
