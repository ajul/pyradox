import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.image
from PIL import Image

scale = 3

# Load states.
states = pyradox.txt.parseMerge(os.path.join(pyradox.config.basedirs['HoI4'], 'history', 'states'))
provinceMap = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.basedirs['HoI4'])

textmap = {}
colormap = {}
for provinceID in provinceMap.positions.keys():
    textmap[provinceID] = '%d' % provinceID
    if provinceMap.isWaterProvince(provinceID):
        colormap[provinceID] = (0, 0, 127)
    else:
        colormap[provinceID] = (0, 0, 0)

out = provinceMap.generateImage({}, defaultLandColor=(255, 255, 255), edgeColor=(191, 191, 191))
out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
provinceMap.overlayText(out, textmap, colormap = colormap, fontfile = "tahoma.ttf", fontsize = 9, antialias = False, defaultOffset = (8, 0))
out.save('out/province_ID_map.png')
#pyradox.image.saveUsingPalette(out, 'out/province_ID_map.png')
