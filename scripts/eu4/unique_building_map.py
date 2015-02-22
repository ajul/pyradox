import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.worldmap

endGame = False

buildingColors = (
    ('tax_assessor', (255, 191, 0)), # gold
    ('embassy', (127, 255, 127)), # green
    ('glorious_monument', (127, 255, 127)), # green
    ('march_building', (127, 255, 127)), # green
    ('grain_depot', (127, 255, 127)), # green
    ('royal_palace', (127, 255, 127)), # green
    ('war_college', (127, 255, 127)), # green
    ('admiralty', (127, 255, 127)), # green
    ('fine_arts_academy', (127, 255, 127)), # green
    ('university', (63, 191, 255)), # blue
    )

colormap = {}
for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces'), verbose=False):
    if endGame:
        data = data.atDate(True)
    else:
        data = data.atDate('1444.11.11')
    m = re.match('\d+', filename)
    provinceID = int(m.group(0))
    color = None
    for building, buildingColor in buildingColors:
        if building in data:
            print(filename, building)
            color = buildingColor
    if color is not None:
        colormap[provinceID] = color
        
provinceMap = pyradox.worldmap.ProvinceMap()
out = provinceMap.generateImage(colormap)
pyradox.image.saveUsingPalette(out, 'out/unique_building_map.png')

