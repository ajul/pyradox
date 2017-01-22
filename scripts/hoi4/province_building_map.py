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

buildingType = 'naval_base'

scale = 2.0

# Load states.
states = pyradox.txt.parseMerge(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'states'), verbose=False)
provinceMap = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.getBasedir('HoI4'))

colormap = {}
textmap = {}

for state in states.values():
    for provinceID, buildings in state['history']['buildings'].items():
        if isinstance(provinceID, int) and buildingType in buildings:
            count = buildings[buildingType]
            textmap[provinceID] = '%d' % count
            colormap[provinceID] = pyradox.image.colormapRedGreen(count / 10)

# Create a blank map and scale it up 2x.
out = provinceMap.generateImage(colormap, defaultLandColor=(255, 255, 255), edgeColor=(191, 191, 191))
# out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
provinceMap.overlayText(out, textmap, fontfile = "tahoma.ttf", fontsize = 9, antialias = False, defaultOffset = (5, -2))
out.save('out/%s_map.png' % buildingType)
#pyradox.image.saveUsingPalette(out, 'out/province_ID_map.png')
