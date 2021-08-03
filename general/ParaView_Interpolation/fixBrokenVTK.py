#!/usr/bin/env python3
import pyvista as pv
import numpy as np
import re
from pathlib import Path
from multiprocessing import Pool
import sys

# Takes different vtk files of the same part and attempts to combine the parts
# that actually have a successful interpolation

###########
# Script Inputs
###########

numparts = 4320
chunksize = 48 # parts per vtm file
basePath = Path('/lus/grand/projects/AdaptVertTR/Models/BoeingBump/DNS/ReL2M/')
outdir = Path('./solnTarget')

PVpartnumMatch = re.compile(r'.*_(\d+)_\d+\.vtu')
batchnumMatch = re.compile(r'.*/?Test\d(\d+)')

TESTONLY = False # Dry-run. Only print out results of merging vtk files
writeIntermediate = False # Write out a vtk file of merged results
readIntermediate = True # Read vtk file of merged results from intermediateOutdir
intermediateOutdir = Path('./IntermediateTest')
intermediateMatch = re.compile(r'.*/?Intermediate_(\d+)\.vtu')

vtmpaths = {
    'Test1' : (basePath / 'Test1', 'Test1*'),
    'Test2' : (basePath / 'Test2', 'Test2*'),
}

worstpaths ={
    'Worst1': (Path('./testWorst'), Path( './testWorst/worst48')),
}

############
# Actually reading and processing data
#############


def loadandwritevtu(filepaths: dict, outdir: Path, phastapartnum: int, writevtu: bool):
    """Writes out a solInterp given a vtu file

    Parameters
    ----------
    filepath : dict
        dict of paths to the vtu file that will be converted
    outdir : Path
        Directory where the solInterp.N file will be saved to
    phastapartnum : int
        Phasta partition number
    writevtu: bool
        Whether to write an Intermediate vtk file
    """

    vtus = {}
    nnodes_list = []
    for key, filepath in filepaths.items():
        try:
            vtus[key] = pv.UnstructuredGrid(filepath)
            nnode = vtus[key].number_of_points
            assert(nnode > 0) # force an exception to be raise if there is
                # an issue reading the vtk file
            nnodes_list.append(vtus[key].number_of_points)
        except Exception as e:
            del vtus[key] #Remove faulty file
            print(f'\tFILE FAILURE: {filepath.name} failed to read correctly for '
                  f'part {phastapartnum}: \n{e}')

    nnodes = list(vtus.values())[0].number_of_points
    for key, vtu in vtus.items():
        assert(vtu.number_of_points == nnodes)

    outdata = np.zeros((nnodes,4))
    mask_filled = np.zeros(nnodes, dtype=np.bool_)
    mask_vtu1d = np.zeros(nnodes, dtype=np.bool_)
    mask_vtu2d = np.zeros((nnodes,4), dtype=np.bool_)
    mask_of_trues = np.ones((nnodes,4), dtype=np.bool_)

    used_node_count = {}
    for key, vtu in vtus.items():
        if np.all(mask_vtu2d): break # stop loop if mask completed

        fileIssue = False
        pressure_keys = ['pressure', 'p']
        if all(array in vtu.array_names for array in ['VelX', 'VelY', 'VelZ', 'vtkValidPointMask']):
            fileIssue = True
        if any(array in vtu.array_names for array in pressure_keys):
            fileIssue = True

        if fileIssue:
            print(f'FILE ISSUE: {filepath.name} does not have expected array names: {vtu.array_names}'
                  f' Skipping file for part {phastapartnum}')
            continue
            sys.stdout.flush()

        for pstr in pressure_keys:
            if pstr in vtu.array_names:
                pressure = pstr
                break

        mask_vtu1d = np.logical_not(mask_filled ** vtu['vtkValidPointMask'])
        used_node_count[key] = np.sum(mask_vtu1d)
        mask_filled = np.logical_or(mask_filled, vtu['vtkValidPointMask'])
        if not TESTONLY:
            dataarray = np.column_stack((vtu[pressure], vtu['VelX'], vtu['VelY'], vtu['VelZ']))
            mask_vtu2d = mask_vtu1d[:,None].astype(np.bool_)*mask_of_trues

            np.copyto(outdata, dataarray, where=mask_vtu2d)

    if not TESTONLY:
        if writevtu:
            vtu = next(iter(vtus.values()))
            vtu[pressure] = outdata[:,0]
            vtu['VelX'] = outdata[:,1]
            vtu['VelY'] = outdata[:,2]
            vtu['VelZ'] = outdata[:,3]
            vtu['vtkValidPointMask'] = mask_filled
            vtu.save(intermediateOutdir / f'Intermediate_{phastapartnum}.vtu')
        else:
            outpath = outdir / f'solInterp.{phastapartnum}'
            np.savetxt(outpath, outdata)

    logstring = '\t'
    for key in vtus.keys():
        if key in used_node_count.keys():
            logstring += f'{key:8}:{used_node_count[key]:8}  '
        else:
            logstring += f'{key:8}: N/A  '

    if not np.all(mask_filled):
        totalpnts = np.sum(np.logical_not(mask_filled))
        percent = totalpnts / nnodes
        print(f'solInterp.{phastapartnum:<5}  BROKEN {totalpnts},{percent:>8.3%}'
              '\n' + logstring)
    else:
        print(f'solInterp.{phastapartnum:<5}  fine'
              '\n' + logstring)
    sys.stdout.flush()


##########
# Create list of files to be processed
##########

    # List of [phastapartnum - 1] = {runkey : vtupath}
interp_vtupaths = [{} for i in range(numparts)]

if readIntermediate:
    for vtu in intermediateOutdir.glob('*.vtu'):
        phastapartnum = int( intermediateMatch.match(vtu.as_posix())[1] )
        interp_vtupaths[phastapartnum - 1]['Intermediate'] = vtu

for runkey, (path, globstr) in vtmpaths.items():
    for vtmdir in path.glob(globstr):
        if not vtmdir.is_dir(): continue
        batchnum =  int( batchnumMatch.match(vtmdir.as_posix())[1] )
        for vtu in vtmdir.glob('*.vtu'):
            pvpartnum =  int( PVpartnumMatch.match(vtu.as_posix())[1] )
            partnum = batchnum*chunksize + pvpartnum
            interp_vtupaths[partnum][runkey] = vtu

for runkey, (vtudir, mapfile) in worstpaths.items():
    partmap = np.loadtxt(mapfile, dtype=int)
    for i, phastapartnum in enumerate(partmap):
        vtupath = list(vtudir.glob(f'*_{i}_*.vtu'))[0]
        interp_vtupaths[phastapartnum - 1][runkey] = vtupath

## Create the pool of processes
with Pool(processes=4) as pool:
    tasks = []
    print('VTU files to be combined')
    for i, pvparts in enumerate(interp_vtupaths):
        partslog = '  '
        for pvpart in pvparts.values():
            partslog += f'{pvpart.name:20} '
        print(partslog)

        tasks.append( pool.apply_async(loadandwritevtu, (pvparts, outdir, i+1, writeIntermediate)) )

    # Wait for tasks to finish
    stats = []
    for t in tasks:
        stats.append(t.get())
