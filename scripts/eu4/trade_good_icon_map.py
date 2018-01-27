import _initpath
import os
import re
import collections

import pyradox
import pyradox.worldmap

import pyradox.image
from PIL import Image

start_date = pyradox.Date('1444.11.11')

# get trade goods
resource_images = pyradox.image.split_strip(Image.open('in/resources.png'))

trade_good_icons = {}
tree = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('EU4'), 'common', 'tradegoods', '00_tradegoods.txt'))
for idx, trade_good in enumerate(tree.keys()):
    trade_good_icons[trade_good] = resource_images[idx]
    resource_images[idx].save('out/tradegoods/trade_good_%s.png' % trade_good)

colormap = {}
iconmap = {}

for filename, data in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('EU4'), 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    province_id = int(m.group(0))
    start_data = data.at_date(start_date)
    # end_data = data.at_date(True)
    if 'base_tax' in data:
        if 'owner' in start_data:
            colormap[province_id] = (191, 191, 191)
        else:
            colormap[province_id] = (127, 127, 127)
        trade_good = 'unknown'
        for curr_good in data.find_walk('trade_goods'):
            if curr_good != 'unknown':
                trade_good = curr_good
        iconmap[province_id] = trade_good_icons[trade_good]
            
        
province_map = pyradox.worldmap.ProvinceMap()
base_map = province_map.generate_image(colormap)
max_size_map = base_map.resize((base_map.size[0] * 4, base_map.size[1] * 4), Image.ANTIALIAS)
province_map.overlay_icons(max_size_map, iconmap)
# max_size_map.save('out/trade_good_icon_map_max.png')

double_size_map = max_size_map.resize((base_map.size[0] * 2, base_map.size[1] * 2), Image.ANTIALIAS)
double_size_map.save('out/trade_good_icon_map_double.png', optimize = True)

regular_size_map = max_size_map.resize((base_map.size[0], base_map.size[1]), Image.ANTIALIAS)
regular_size_map.save('out/trade_good_icon_map.png', optimize = True)
