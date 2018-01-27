import hoi4
import os
import re
import collections

import pyradox


from PIL import Image

scale = 2.0

# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'states'))
province_map = pyradox.worldmap.ProvinceMap(game = 'HoI4')

# provinces -> state id
groups = {}

for state in states.values():
    k = tuple(province_id for province_id in state.find_all('provinces') if not province_map.is_water_province(province_id))
    groups[k] = str(state['id'])

out = province_map.generate_image({}, default_land_color=(255, 255, 255), edge_color=(191, 191, 191), edge_groups = groups.keys())
# out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
province_map.overlay_text(out, groups, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/state__id_map.png')
#pyradox.image.save_using_palette(out, 'out/province__id_map.png')
