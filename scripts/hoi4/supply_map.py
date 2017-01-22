import _initpath
import os
import math
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.image
from PIL import Image

scale = 2.0

# Load states.
states = pyradox.txt.parseMerge(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'states'), verbose=False)
supplyAreas = pyradox.txt.parseMerge(os.path.join(pyradox.config.getBasedir('HoI4'), 'map', 'supplyareas'), verbose=False)

statesByID = {state['id'] : state for state in states.values()}

# supplyAreaID -> provinceIDs
supplyAreaProvinces = {}
supplyAreaLocalSupply = {}
supplyAreaTransport = {}

for supplyArea in supplyAreas.values():
    supplyAreaProvinces[supplyArea['id']] = []
    
    totalInfrastructure = 0
    totalVPSupply = 0
    totalNavalBase = 0
    
    for stateID in supplyArea.findAll('states'):
        state = statesByID[stateID]
        if 'buildings' in state['history']:
            totalInfrastructure += state['history']['buildings']['infrastructure']
            for k, v in state['history']['buildings'].items():
                if isinstance(k, int):
                    totalNavalBase += v['naval_base'] or 0
        
        for provinceID in state.findAll('provinces'):
            supplyAreaProvinces[supplyArea['id']].append(provinceID)

        for _, vpValue in state['history'].findAll('victory_points', tupleLength = 2):
            totalVPSupply += math.floor(vpValue * 0.1 + 1)
            
    averageInfrastructure = totalInfrastructure / supplyArea.count('states')
    infrastructureTransport = 2.0 * (averageInfrastructure ** 2.0)
    navalTransport = 3.0 * totalNavalBase
    transport = max(infrastructureTransport, navalTransport)
    
    localSupply = supplyArea['value'] + totalVPSupply
    supplyAreaLocalSupply[supplyArea['id']] = localSupply
    supplyAreaTransport[supplyArea['id']] = transport

provinceMap = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.getBasedir('HoI4'))

# provinces -> state id
groupsLocal = {}
colormapLocal = {}
groupsTransport = {}
colormapTransport = {}

for supplyAreaID, provinces in supplyAreaProvinces.items():
    localSupply = supplyAreaLocalSupply[supplyAreaID]
    transport = supplyAreaTransport[supplyAreaID]
    k = []
    for provinceID in provinces:
        if not provinceMap.isWaterProvince(provinceID):
            k.append(provinceID)
            colormapLocal[provinceID] = pyradox.image.colormapRedGreen(localSupply / 25)
            colormapTransport[provinceID] = pyradox.image.colormapRedGreen(transport / 100)
    k = tuple(x for x in k)
    groupsLocal[k] = '%d' % localSupply
    groupsTransport[k] = '%d' % transport

localImage = provinceMap.generateImage(colormapLocal, defaultLandColor=(255, 255, 255), edgeColor=(63, 63, 63), edgeGroups = groupsLocal.keys())
provinceMap.overlayText(localImage, groupsLocal, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
localImage.save('out/local_supply_map.png')

transportImage = provinceMap.generateImage(colormapTransport, defaultLandColor=(255, 255, 255), edgeColor=(63, 63, 63), edgeGroups = groupsTransport.keys())
provinceMap.overlayText(transportImage, groupsTransport, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
transportImage.save('out/transport_supply_map.png')

