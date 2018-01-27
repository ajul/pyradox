import _initpath
import os
import re
import collections
from PIL import Image
import pyradox.config
import pyradox.txt
import pyradox.worldmap

tree = pyradox.txt.parse_file(os.path.join(pyradox.config.get_game_directory('EU4'), 'map', 'terrain.txt'))

terrain_bmp = Image.open(os.path.join(pyradox.config.get_game_directory('EU4'), 'map', 'terrain.bmp'))
print(terrain_bmp.getpalette())

province_map = pyradox.worldmap.ProvinceMap()

colormap = {}

for province_id, position in province_map.positions.items():
    print(province_id)
    colormap[province_id] = tuple(terrain_bmp.getpixel(position))

for terrain_type, terrain_data in tree['categories'].items():
    if 'color' not in terrain_data: continue
    color = tuple(terrain_data.find_all('color'))
    for province_id in terrain_data.find_all('terrain_override'):
        colormap[province_id] = color


out = province_map.generate_image(colormap)
out.save('out/terrain_map.png')
