import _initpath
import os
import re
import collections

import pyradox


from PIL import Image

# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'states'), verbose=False)

# provinces -> state id
groups = {}

for state in states.values():
    k = tuple(province_id for province_id in state.find_all('provinces'))
    groups[k] = str(state['id'])

# Load the province map using the default location set in pyradox.
province_map = pyradox.worldmap.ProvinceMap(basedir = pyradox.get_game_directory('HoI4'))

out = province_map.generate_image({}, default_land_color=(255, 255, 255), edge_groups = groups.keys())

pyradox.image.save_using_palette(out, 'out/blank_state_map.png')
