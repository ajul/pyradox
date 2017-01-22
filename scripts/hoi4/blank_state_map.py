import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.image
from PIL import Image

# Load states.
states = pyradox.txt.parseMerge(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'states'), verbose=False)

# provinces -> state id
groups = {}

for state in states.values():
    k = tuple(provinceID for provinceID in state.findAll('provinces'))
    groups[k] = str(state['id'])

# Load the province map using the default location set in pyradox.config.
provinceMap = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.getBasedir('HoI4'))

out = provinceMap.generateImage({}, defaultLandColor=(255, 255, 255), edgeGroups = groups.keys())

pyradox.image.saveUsingPalette(out, 'out/blank_state_map.png')
