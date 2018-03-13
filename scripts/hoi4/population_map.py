import hoi4
import os
import math
import re
import collections

import pyradox


from PIL import Image

scale = 2.0

# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'states'), verbose=False)
province_map = pyradox.worldmap.ProvinceMap(game = 'HoI4')

# provinces -> state id
groups = {}
colormap = {}

for state in states.values():
    population = state['manpower'] or 0
    if population >= 1e6:
        population_string = "%0.1fM" % (population / 1e6)
    elif population >= 1e3:
        population_string = "%0.1fk" % (population / 1e3)
    else:
        population_string = "%d" % population

    k = []
    for province_id in state.find_all('provinces'):
        if not province_map.is_water_province(province_id):
            k.append(province_id)
            colormap[province_id] = pyradox.image.colormap_red_green(population / 10e6)
    k = tuple(x for x in k)
    groups[k] = population_string



# Create a blank map and scale it up 2x.
out = province_map.generate_image(colormap, default_land_color=(255, 255, 255), edge_color=(191, 191, 191), edge_groups = groups.keys())
# out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
province_map.overlay_text(out, groups, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/population_map.png')
#pyradox.image.save_using_palette(out, 'out/province__id_map.png')
