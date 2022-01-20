#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()
import os, copy, sys


#pluginPath = '/projects/PHASTA_aesp/ParaView/ParaViewSyncIOReaderPlugin/build541/libPhastaSyncIOReader.so'
#pluginPath = '/grand/AdaptVertTR/ParaView/ParaViewSyncIOReaderPlugin/build5p91/lib64/PhastaSyncIOReader/PhastaSyncIOReader.so'
pluginPath = '/soft/visualization/paraview/v5.9.1//lib/paraview-5.9/plugins/PhastaSyncIOReader/PhastaSyncIOReader.so'
phtsPath = './template.phts'  #using the word template because, like the interpolation code, we are going to loop over time steps and soft link files into a directory that this phts points at for our time step looping.  Note we do this because have thus far been unsuccesful getting pvbatch to cooperate with a multi time step phts file

Lz=0.1424
Nz=6809
nSyncIO = 243
nParts = 155520
templateStepN=125000  # currently hard coded but need to get his to be controlled from this too.
procs_dir = './template-procs_case'
timestepfile = 'timesteps'
locationsfile = 'locations'


locations = {}
with open(locationsfile) as f:
    for line in f:
        linelist = line.split()
        if len(linelist) < 1:
            continue
        elif linelist[0][0] == '#':
            continue
        else:
            locations[linelist[0]] = [float(x) for x in linelist[1:]]

for key, value in locations.items():
    print(key, value)



print('Loading Plugin...')
LoadPlugin(pluginPath, remote=True, ns=globals())
print(' Done!')

timesteps = open(timestepfile).read().split('\n')
scratch_timesteps = copy.deepcopy(timesteps)

for j, stimestep in enumerate(timesteps):
    print(stimestep)
    if stimestep == '': continue

    os.chdir(procs_dir)
    for i in range(nSyncIO):
        target = 'restart-dat.125000.' + str(i+1)
        if os.path.islink(target):
            os.remove(target)
#        os.symlink('../../{}-procs_case/restart-dat.{}.{}'.format(nParts,stimestep, i+1), target)
        os.symlink('../{}-procs_case/restart-dat.{}.{}'.format(nParts,stimestep, i+1), target)
    os.chdir(r"..")

#    if j == 0:
    if j >= 0:
        # create a new 'Phasta SyncIO Reader'
        print ('Loading phts...')
        templatephts = PhastaSyncIOReader(FileName=phtsPath)
        print(' about to update pipeline ')
        UpdatePipeline(time=0.0,proxy=templatephts)
        print(' Done!')

        # create a new 'Plot Over Line'
        print ('Create plotOverLine...')
        plotOverLine1 = PlotOverLine(Input=templatephts,
            Source='High Resolution Line Source')
        print (' Done!')
#    else:
#        print ('Reloading phts...')
#        ReloadFiles(templatephts)
#        UpdatePipeline(time=0.0,proxy=templatephts)
#        templatephts.UpdatePipeline()
#        print(' Done!')

    print ('    Looping over locations: ')
    for key, point in locations.items():
        print (str(key))
        # Properties modified on plotOverLine1.Source
        plotOverLine1.Source.Point1 = [point[0], point[1], 0.0]
        plotOverLine1.Source.Point2 = [point[0], point[1], Lz]
        plotOverLine1.Source.Resolution = Nz

        # Properties modified on plotOverLine1
        plotOverLine1.Tolerance = 2.22044604925031e-16

        filename = '-'.join([key, stimestep]) + '.csv'

        SaveData('./spectra_csvs/' + filename, proxy=plotOverLine1, Precision=16, UseScientificNotation=1)

    print (' Done!')
# destroy plotOverLine1
    Delete(plotOverLine1)
    del plotOverLine1

# destroy templatephts
    Delete(templatephts)
    del templatephts

    for i in range(nSyncIO):
        os.remove(procs_dir + '/restart-dat.125000.' + str(i+1))

    scratch_timesteps.remove(str(stimestep))
    print('Done timestep ' + str(stimestep) + '. Left to go: ' + ' '.join(scratch_timesteps))
    with open(timestepfile, 'w') as f:
        f.write('\n'.join(scratch_timesteps))

if len(timesteps) == 1 and timesteps[0] == '':
    print('The timesteps file is empty. Exiting now')
    sys.exit(1)
