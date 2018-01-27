import _initpath
import os
import math
import re
import collections
import pyradox.config
import pyradox
import pyradox.worldmap
import pyradox.image
from PIL import Image

scale = 2.0

colormap_power = 1.0

# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.config.get_game_directory('HoI4'), 'history', 'states'), verbose=False)
province_map = pyradox.worldmap.ProvinceMap(game = 'HoI4')

# provinces -> state id
groups = {}
colormap = {}

for state in states.values():
    if 'history' not in state:
        print('State missing history:')
        print(state)
        infrastructure = 0
    elif 'buildings' not in state['history']:
        print('State missing buildings:')
        print(state)
        infrastructure = 0
    else:
        infrastructure = state['history']['buildings']['infrastructure']

    k = []
    for province_id in state.find_all('provinces'):
        if not province_map.is_water_province(province_id):
            k.append(province_id)
            x = (infrastructure / 9.0) ** colormap_power
            colormap[province_id] = pyradox.image.colormap_red_green(x)
    k = tuple(x for x in k)
    groups[k] = '%d' % infrastructure



# Create a blank map and scale it up 2x.
out = province_map.generate_image(colormap, default_land_color=(255, 255, 255), edge_color=(191, 191, 191), edge_groups = groups.keys())
# out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
province_map.overlay_text(out, groups, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/infrastructure_map.png')
#pyradox.image.save_using_palette(out, 'out/province__id_map.png')
