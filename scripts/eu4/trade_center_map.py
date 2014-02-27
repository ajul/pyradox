import initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap

colormap = {}
for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    provinceID = int(m.group(0))
    modifierValue = 0
    for modifier in data.findWalk('add_permanent_province_modifier'):
        if modifier['name'] in ('bosphorous_sound_toll', 'sound_toll', 'rhine_estuary_modifier'):
            modifierValue += 2
        else:
            modifierValue += 1
    if modifierValue == 1:
        # bronze
        colormap[provinceID] = (127, 63, 0)
    elif modifierValue == 2:
        # silver
        colormap[provinceID] = (191, 191, 191)
    elif modifierValue >= 3:
        # gold
        colormap[provinceID] = (255, 191, 0)
        
provinceMap = pyradox.worldmap.ProvinceMap()
out = provinceMap.generateImage(colormap)
out.save('out/trade_center_map.png')

