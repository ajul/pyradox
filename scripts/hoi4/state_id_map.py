import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.image
from PIL import Image

scale = 2.0

# Load states.
states = pyradox.txt.parseMerge(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'states'))
provinceMap = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.getBasedir('HoI4'))

# provinces -> state id
groups = {}

for state in states.values():
    k = tuple(provinceID for provinceID in state.findAll('provinces') if not provinceMap.isWaterProvince(provinceID))
    groups[k] = str(state['id'])

out = provinceMap.generateImage({}, defaultLandColor=(255, 255, 255), edgeColor=(191, 191, 191), edgeGroups = groups.keys())
# out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
provinceMap.overlayText(out, groups, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/state_ID_map.png')
#pyradox.image.saveUsingPalette(out, 'out/province_ID_map.png')
