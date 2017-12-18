import _initpath
import os
import re
import collections
from PIL import Image
import pyradox.config
import pyradox.txt
import pyradox.worldmap

tree = pyradox.txt.parseFile(os.path.join(pyradox.config.getBasedir('EU4'), 'map', 'terrain.txt'))

terrain_bmp = Image.open(os.path.join(pyradox.config.getBasedir('EU4'), 'map', 'terrain.bmp'))
print(terrain_bmp.getpalette())

provinceMap = pyradox.worldmap.ProvinceMap()

colormap = {}

for provinceID, position in provinceMap.positions.items():
    print(provinceID)
    colormap[provinceID] = tuple(terrain_bmp.getpixel(position))

for terrain_type, terrain_data in tree['categories'].items():
    if 'color' not in terrain_data: continue
    color = tuple(terrain_data.findAll('color'))
    for provinceID in terrain_data.findAll('terrain_override'):
        colormap[provinceID] = color


out = provinceMap.generateImage(colormap)
out.save('out/terrain_map.png')
