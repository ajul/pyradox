import _initpath

import pyradox

import os
from PIL import Image

province_map = pyradox.worldmap.ProvinceMap()
terrain_map_image = Image.open('in/terrain.png')
terrain_txt = pyradox.txt.parse_file(os.path.join(os.path.join(pyradox.get_game_directory('EU4'), 'map', 'terrain.txt')))

terrain_by_color = {}

for terrain_name, terrain in terrain_txt['categories'].items():
    if 'color' in terrain:
        color = tuple(terrain['color'])
        terrain_by_color[color] = (terrain_name, terrain)

def get_province_terrain(province_id):
    position = province_map.positions[province_id]
    color = terrain_map_image.getpixel(position)
    return terrain_by_color[tuple(color)]
