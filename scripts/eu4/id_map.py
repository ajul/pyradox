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

colormap = {}
for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('EU4'), 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    provinceID = int(m.group(0))
    if ('base_tax' in data and data['base_tax'] > 0):
        colormap[provinceID] = (150, 150, 150)

# Create a blank map and scale it up 2x.
out = provinceMap.generateImage(colormap, defaultLandColor=(97, 97, 97), defaultWaterColor=(68, 107, 163), edgeColor=(255, 255, 255))
out = out.resize((out.size[0] * 2, out.size[1] * 2), Image.NEAREST)

# Create the map labels.
textmap = {}
colormap = {}
for provinceID in provinceMap.positions.keys():
    textmap[provinceID] = '%d' % provinceID
    if provinceMap.isWaterProvince(provinceID):
        colormap[provinceID] = (0, 0, 0)
    else:
        colormap[provinceID] = (0, 0, 0)

provinceMap.overlayText(out, textmap, colormap = colormap, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/province_ID_map.png')
#pyradox.image.saveUsingPalette(out, 'out/province_ID_map.png')
