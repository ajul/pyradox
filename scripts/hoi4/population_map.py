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
provinceMap = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.getBasedir('HoI4'))

# provinces -> state id
groups = {}
colormap = {}

for state in states.values():
    population = state['manpower'] or 0
    if population >= 1e6:
        populationString = "%0.1fM" % (population / 1e6)
    elif population >= 1e3:
        populationString = "%0.1fk" % (population / 1e3)
    else:
        populationString = "%d" % population

    k = []
    for provinceID in state.findAll('provinces'):
        if not provinceMap.isWaterProvince(provinceID):
            k.append(provinceID)
            colormap[provinceID] = pyradox.image.colormapRedGreen(population / 10e6)
    k = tuple(x for x in k)
    groups[k] = populationString



# Create a blank map and scale it up 2x.
out = provinceMap.generateImage(colormap, defaultLandColor=(255, 255, 255), edgeColor=(191, 191, 191), edgeGroups = groups.keys())
# out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
provinceMap.overlayText(out, groups, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/population_map.png')
#pyradox.image.saveUsingPalette(out, 'out/province_ID_map.png')
