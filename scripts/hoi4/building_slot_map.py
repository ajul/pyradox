import _initpath
import os
import math
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.image
from PIL import Image

# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.config.get_basedir('HoI4'), 'history', 'states'), verbose=False)
state_categories = pyradox.txt.parse_merge(os.path.join(pyradox.config.get_basedir('HoI4'), 'common', 'state_category'), verbose=False)
province_map = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.get_basedir('HoI4'))

# provinces -> state id
groups = {}
colormap = {}

for state in states.values():
    state_category_key = state['state_category']
    building_slots = state_categories[state_category_key]['local_building_slots'] or 0

    k = []
    for province_id in state['provinces']:
        if not province_map.is_water_province(province_id):
            k.append(province_id)
            colormap[province_id] = pyradox.image.colormap_red_green(building_slots / 10)
    k = tuple(x for x in k)
    groups[k] = '%d' % building_slots


# Create a blank map and scale it up 2x.
out = province_map.generate_image(colormap, default_land_color=(255, 255, 255), edge_color=(191, 191, 191), edge_groups = groups.keys())
# out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
province_map.overlay_text(out, groups, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/building_slot_map.png')
#pyradox.image.save_using_palette(out, 'out/province__id_map.png')
