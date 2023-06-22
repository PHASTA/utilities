#!/usr/bin/env python3
import pyvista as pv
import numpy as np
import re
from pathlib import Path
from multiprocessing import Pool

###########
# Script Inputs
###########

    # Number of parts per batch interpolated by Paraview
chunksize = 100

    ## Base path for everything below. Just so this script can be placed whereever desired
basePath = Path('/lus/grand/projects/AdaptVertTR/Models/BoeingBump/DNS/ReL2M/')

    ## Path where the *.vtm files are located.
    # We'll glob this directory for the subdirectories containing *.vtu files
vtmPath = basePath
# vtmPath = basePath / Path('../../relative/path/to/directory') # to point to different directory

    ## Path to where solInterp files should be dumped
# outputDir = basePath / Path('solnTarget')
outputDir = Path('solnTarget') # For testing

    ## Regular expression to get the part number according to vtk
    # The `(\d+)` is the matching group, so that is what will be interpreted as
    # the batch number. Everything else is just to make sure we get the correct
    # number
PVpartnumMatch = re.compile(r'.*_(\d+)_\d+\.vtu')

    ## Regular expression to get the batch number from the vtm directory name.
    # Same basic idea as above with regards to `(\d+)`.
batchnumMatch = re.compile(r'.*/Test1(\d+)')

########
# Collecting directories to search for vtus
########

# Create list of "vtm" directories
vtmdirs = []
for vtmdir in vtmPath.glob('Test1*'):
    if vtmdir.is_dir():
        vtmdirs.append(vtmdir)

print('The following directories will be used to find *.vtu files:')
for vtmdir in vtmdirs:
    print('\t' + vtmdir.as_posix())

############
# Actually reading and processing data
#############

def loadandwritevtu(filepath: Path, outdir: Path, batchnum: int, chunksize: int):
    """Writes out a solInterp given a vtu file

    Parameters
    ----------
    filepath : Path
        Path to the vtu file that will be converted
    outdir : Path
        Directory where the solInterp.N file will be saved to
    batchnum : int
        The batch number. Assumed to start at 0
    chunksize : int
        The number of partitions per batch
    """
    vtu = pv.UnstructuredGrid(filepath)

        ## Paraview part number. Increments from 0
    PVpartnum = PVpartnumMatch.match(filepath.as_posix())[1]

        ## Phasta part number. Increments from 1
    phastaPartNum = batchnum*chunksize + int(PVpartnum) + 1

    print(f'Converting {filepath.name:18} -> solInterp.{phastaPartNum}')

        ## Path to where solInterp.{phastaPartNum} should be saved.
    outpath = outdir / f'solInterp.{phastaPartNum}'

        ## Saves the file into ASCII
        # Note that vtu.points is of shape (nnodes, 3), while all else is just
        # (nnodes)
# classic way includes coordinates    np.savetxt(outpath, np.column_stack((vtu.points, vtu['pressure'], vtu['VelX'], vtu['VelY'], vtu['VelZ'])))
#for planned converter in phInterp will enable a lighter/faster option of
#trusting the points are right and just use solution
    np.savetxt(outpath, np.column_stack((vtu['pressure'], vtu['VelX'], vtu['VelY'], vtu['VelZ'])))


## The parallel processing here is conceptually identical to OpenMP tasks (if
# you're familiar with that). Effective, I get a pool of processes and create a
# list of tasks for it to do. Each process will grab a task from the list and
# complete it. Once a process is done with a task, it'll ask for another task
# to complete. This continues until all the tasks are done.

# If you run into memory issues, simply reduce the number of proceses to reduce
# number of concurrent tasks being run.
# Note that this is only for one node. Giving it anymore nodes won't do
# anything.

## Create the pool of processes
with Pool(processes=12) as pool:

    tasks = []
    for vtmdir in vtmdirs:
            ## Get the batch number from the name of the directory
        batchnum = int( batchnumMatch.match(vtmdir.as_posix())[1] )
            ## Loop through vtu files matching the glob
        for vtu in vtmdir.glob('*.vtu'):
            # This creates the set of tasks the pool should execute. The
            # `loadandwritevtu` specifies the function to run and the `(vtu,
            # outputDir, ...)` gives the arguments that should be given to the
            # function for this task.
            tasks.append(pool.apply_async(loadandwritevtu, (vtu, outputDir, batchnum, chunksize)))

    # Wait for tasks to finish
    [t.get() for t in tasks]
