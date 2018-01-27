import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.image
from PIL import Image

scale = 3

# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.config.get_game_directory('HoI4'), 'history', 'states'))
srs = pyradox.txt.parse_merge(os.path.join(pyradox.config.get_game_directory('HoI4'), 'map', 'strategicregions'))
province_map = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.get_game_directory('HoI4'))

# state id -> provinces
state_groups = {}

for state in states.values():
    group = tuple(province_id for province_id in state.find_all('provinces'))
    if len(group) > 0: state_groups[state['id']] = group

sr_groups = []

for sr in srs.values():
    # may have empty group
    group = tuple(province_id for province_id in sr.find_all('provinces') if isinstance(province_id, int))
    if len(group) > 0: sr_groups.append(group)

textmap = {}
colormap = {}
for province_id in province_map.positions.keys():
    textmap[province_id] = '%d' % province_id
    if province_map.is_water_province(province_id):
        colormap[province_id] = (0, 0, 127)
    else:
        colormap[province_id] = (0, 0, 0)

out = province_map.generate_image({}, default_land_color=(255, 255, 255), edge_color=(191, 191, 191))
province_map.overlay_edges(out, edge_color=(255, 191, 191), groups=state_groups.values())
province_map.overlay_edges(out, edge_color=(255, 63, 63), groups=sr_groups)
out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
province_map.overlay_text(out, textmap, colormap = colormap, fontfile = "tahoma.ttf", fontsize = 9, antialias = False, default_offset = (8, 0))
out.save('out/province__id_map.png')
#pyradox.image.save_using_palette(out, 'out/province__id_map.png')
