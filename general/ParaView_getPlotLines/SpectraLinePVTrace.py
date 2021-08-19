#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()
import os, copy, sys


pluginPath = '/projects/PHASTA_aesp/ParaView/ParaViewSyncIOReaderPlugin/build541/libPhastaSyncIOReader.so'
phtsPath = './CRS_4delta_6-15_28000.phts'

nSyncIO = 20
procs_dir = './spectra-procs_case'
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



print 'Loading Plugin...',
LoadPlugin(pluginPath, remote=True, ns=globals())
print(' Done!')

timesteps = open(timestepfile).read().split('\n')
scratch_timesteps = copy.deepcopy(timesteps)

for j, stimestep in enumerate(timesteps):
    print(stimestep)
    if stimestep == '': continue

    os.chdir(procs_dir)
    for i in range(nSyncIO):
        target = 'restart-dat.28000.' + str(i+1)
        if os.path.islink(target):
            os.remove(target)
        os.symlink('../../1920-procs_case/restart-dat.{}.{}'.format(stimestep, i+1), target)
    os.chdir(r"..")

    if j == 0:
        # create a new 'Phasta SyncIO Reader'
        print 'Loading phts...',
        cRS_4delta_615_28000phts = PhastaSyncIOReader(FileName=phtsPath)
        cRS_4delta_615_28000phts.UpdatePipeline()
        print(' Done!')

        # create a new 'Plot Over Line'
        print 'Create plotOverLine...',
        plotOverLine1 = PlotOverLine(Input=cRS_4delta_615_28000phts,
            Source='High Resolution Line Source')
        print ' Done!'
    else:
        print 'Reloading phts...',
        ReloadFiles(cRS_4delta_615_28000phts)
        cRS_4delta_615_28000phts.UpdatePipeline()
        print(' Done!')

    print '    Looping over locations: ',
    for key, point in locations.items():
        print str(key),
        # Properties modified on plotOverLine1.Source
        plotOverLine1.Source.Point1 = [point[0], point[1], 0.0]
        plotOverLine1.Source.Point2 = [point[0], point[1], 0.452]
        plotOverLine1.Source.Resolution = 1029 #258 + 247*3

        # Properties modified on plotOverLine1
        plotOverLine1.Tolerance = 2.22044604925031e-16

        filename = '-'.join([key, stimestep]) + '.csv'

        SaveData('./spectra_csvs/' + filename, proxy=plotOverLine1, Precision=16, UseScientificNotation=1)

    print ' Done!'

    for i in range(nSyncIO):
        os.remove(procs_dir + '/restart-dat.28000.' + str(i+1))

    scratch_timesteps.remove(str(stimestep))
    print('Done timestep ' + str(stimestep) + '. Left to go: ' + ' '.join(scratch_timesteps))
    with open(timestepfile, 'w') as f:
        f.write('\n'.join(scratch_timesteps))

if len(timesteps) == 1 and timesteps[0] == '':
    print('The timesteps file is empty. Exiting now')
    sys.exit(1)

# destroy plotOverLine1
Delete(plotOverLine1)
del plotOverLine1

# destroy cRS_4delta_615_28000phts
Delete(cRS_4delta_615_28000phts)
del cRS_4delta_615_28000phts
