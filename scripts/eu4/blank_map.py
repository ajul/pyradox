import _initpath
import os
import re
import collections


import pyradox

        
province_map = pyradox.worldmap.ProvinceMap(game = 'EU4')

colormap = {}
for filename, data in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('EU4'), 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    province_id = int(m.group(0))
    if ('base_tax' in data and data['base_tax'] > 0):
        colormap[province_id] = (255, 255, 255)

out = province_map.generate_image(colormap, default_land_color=(95, 95, 95))
pyradox.image.save_using_palette(out, 'out/blank_map.png')
