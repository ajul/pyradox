import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.image
from PIL import Image

# Load the province map using the default location set in pyradox.config.
provinceMap = pyradox.worldmap.ProvinceMap()

# Create a blank map and scale it up 2x.
out = provinceMap.generateImage({}, defaultLandColor=(127, 127, 127), defaultWaterColor=(127, 127, 255), edgeColor=(255, 255, 255))
out = out.resize((out.size[0] * 2, out.size[1] * 2), Image.NEAREST)

# Create the map labels.
textmap = {}
colormap = {}
for provinceID in provinceMap.positions.keys():
    textmap[provinceID] = '%d' % provinceID
    if provinceMap.isWaterProvince(provinceID):
        colormap[provinceID] = (0, 0, 127)
    else:
        colormap[provinceID] = (0, 0, 0)

provinceMap.overlayText(out, textmap, colormap = colormap, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/province_ID_map.png')
#pyradox.image.saveUsingPalette(out, 'out/province_ID_map.png')
