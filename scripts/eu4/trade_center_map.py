import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.worldmap

colors = (
    ('', (127, 0, 255)), # purple
    ('trade', (191, 191, 191)), # silver
    ('estuary', (0, 255, 255)), # teal
    ('toll', (255, 191, 0)), # gold
    ('religious', (255, 0, 0)), # red
    )

colormap = {}
for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    provinceID = int(m.group(0))
    provinceValue = -1
    for modifier in data.findAll('add_permanent_province_modifier', recurse=True):
        for x, (s, color) in enumerate(colors):
            if s in modifier['name']:
                provinceValue = max(provinceValue, x)
    if provinceValue > -1:
        colormap[provinceID] = colors[provinceValue][1]
        
provinceMap = pyradox.worldmap.ProvinceMap()
out = provinceMap.generateImage(colormap)
pyradox.image.saveUsingPalette(out, 'out/trade_center_map.png')

