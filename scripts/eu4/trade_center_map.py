import _initpath
import os
import re
import collections

import pyradox.image
import pyradox
import pyradox.worldmap

colors = (
    ('', (127, 0, 255)), # purple
    ('trade', (191, 191, 191)), # silver
    ('estuary', (0, 255, 255)), # teal
    ('toll', (255, 191, 0)), # gold
    ('religious', (255, 0, 0)), # red
    )

colormap = {}
for filename, data in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('EU4'), 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    province_id = int(m.group(0))
    province_value = -1
    for modifier in data.find_all('add_permanent_province_modifier', recurse=True):
        for x, (s, color) in enumerate(colors):
            if s in modifier['name']:
                province_value = max(province_value, x)
    if province_value > -1:
        colormap[province_id] = colors[province_value][1]
        
province_map = pyradox.worldmap.ProvinceMap()
out = province_map.generate_image(colormap)
pyradox.image.save_using_palette(out, 'out/trade_center_map.png')

