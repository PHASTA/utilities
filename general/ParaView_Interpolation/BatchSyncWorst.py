# trace generated using paraview version 5.5.2-1-g59c2b72f15

#### import the simple module from the paraview
from paraview.simple import *
import os
import copy
print('done importing')

#vtm sourceDoubleDomain = XMLMultiBlockDataReader(FileName=['/grand/AdaptVertTR/Models/BoeingBump/DNS/ReL2M/Interp52and58/52_58p4_GroupDataSet.vtm'])
#print("source file loaded \n ")

# back to load and compute since vtm seems to have more errors

GrowSourceDomain = 0 
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# load plugin
LoadPlugin('/grand/AdaptVertTR/ParaView/ParaViewSyncIOReaderPlugin/build552/libPhastaSyncIOReader.so', remote=True, ns=globals())


# create a new 'Phasta SyncIO Reader'
dNS_58kphts = PhastaSyncIOReader(FileName='/grand/AdaptVertTR/Models/BoeingBump/DNS/ReL2M/RunDNS_38k/DNS_58k.phts')
#dNS_58kphts = XMLMultiBlockDataReader(FileName=['/grand/AdaptVertTR/Models/BoeingBump/DNS/ReL2M/RunDNS_38k/58kDNS.vtm'])
print("58k file loaded \n ")


# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [1731, 993]

# show data in view
dNS_58kphtsDisplay = Show(dNS_58kphts, renderView1)
print("show 58k file loaded \n ")

# reset view to fit data
renderView1.ResetCamera()

# update the view to ensure updated data information
renderView1.Update()

if GrowSourceDomain > 0 :
# create a new 'Transform' HACK_KEJ_Start
    transform2 = Transform(Input=dNS_58kphts)
    transform2.Transform = 'Transform'

# Properties modified on transform1.Transform
#    transform2.Transform.Scale = [GrowSourceDomain, GrowSourceDomain, GrowSourceDomain]
    transform2.Transform.Scale = [1.00000, 1.00000, GrowSourceDomain]

# show data in view
    transform2Display = Show(transform2, renderView1)
    print("show scale \n ")
    calculator1 = Calculator(Input=transform2)
else:
    calculator1 = Calculator(Input=dNS_58kphts)


# continue the create a new 'Calculator'
calculator1.Function = ''

# Properties modified on calculator1
calculator1.ResultArrayName = 'VelX'
calculator1.Function = 'u_X'

# show data in view
calculator1Display = Show(calculator1, renderView1)
print("show calculate \n ")


# update the view to ensure updated data information
renderView1.Update()

# create a new 'Calculator'
calculator2 = Calculator(Input=calculator1)
calculator2.Function = ''

# Properties modified on calculator2
calculator2.ResultArrayName = 'VelY'
calculator2.Function = 'u_Y'

# show data in view
calculator2Display = Show(calculator2, renderView1)
print("show calculate \n ")

# hide data in view
Hide(calculator1, renderView1)

# update the view to ensure updated data information
renderView1.Update()

# create a new 'Calculator'
calculator3 = Calculator(Input=calculator2)
calculator3.Function = ''

# Properties modified on calculator3
calculator3.ResultArrayName = 'VelZ'
calculator3.Function = 'u_Z'

# show data in view
calculator3Display = Show(calculator3, renderView1)
print("show calculate \n ")

# hide data in view
Hide(calculator2, renderView1)

# update the view to ensure updated data information
renderView1.Update()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# show data in view
#vtm sourceDoubleDomainDisplay = Show(sourceDoubleDomain, renderView1)
print("show source file loaded \n ")


phtfile = './Worst.pht'

# create a new 'Phasta Reader'
print("pht file about to load \n ")
#Batchpht = PhastaReader(FileName='/grand/AdaptVertTR/Models/BoeingBump/DNS/ReL2M/Batch.pht')
Batchpht = PhastaReader(FileName=phtfile)
#    Batchpht = PhastaReader(FileName='./Batch3.pht')

# show data in view
BatchphtDisplay = Show(Batchpht, renderView1)

print("pht file loaded \n ")

# create a new 'Resample With Dataset'
resampleWithDataset1 = ResampleWithDataset(Input=calculator3,
Source=Batchpht)
resampleWithDataset1.CellLocator = 'Static Cell Locator'
 # Properties modified on resampleWithDataset1
#resampleWithDataset1.ComputeTolerance = 0
#resampleWithDataset1.Tolerance = 2.0e-16

print("Resample setup \n ")
resampleWithDataset1Display = Show(resampleWithDataset1, renderView1)

# save data
SaveData('./Worst' + str(sys.argv[1]) + '.vtm', proxy=resampleWithDataset1)
