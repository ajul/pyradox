import _initpath
import os
import re
import collections

import pyradox


from PIL import Image

def compute_country_tag(filename):
    m = re.match('.*([A-Z]{3})\s*-.*\.txt$', filename)
    return m.group(1)

def compute_color(values):
    if isinstance(values[0], int):
        # rgb
        r = values[0]
        g = values[1]
        b = values[2]
        return (r, g, b)
    else:
        # hsv
        return pyradox.image.HSVtoRGB(values)
     

date = pyradox.Date('1936.1.1')
scale = 2.0

# state_id -> [tag]
capital_states = {}
country_colors = {}

country_color_file = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('HoI4'), 'common', 'countries', 'colors.txt'))

for filename, country in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'countries')):
    tag = compute_country_tag(filename)
    if tag in country_color_file:
        country_colors[tag] = compute_color(tuple(country_color_file[tag].find_all('color')))
    else:
        print('HACK FOR %s' % tag)
        country_colors[tag] = (165, 102, 152)
    print(tag, country_colors[tag])
    if country['capital'] not in capital_states: capital_states[country['capital']] = []
    capital_states[country['capital']].append(tag)

# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'states'))
province_map = pyradox.worldmap.ProvinceMap(basedir = pyradox.get_game_directory('HoI4'))

# provinces -> state id
colormap = {}
textcolormap = {}
groups = {}

for state in states.values():
    k = tuple(province_id for province_id in state.find_all('provinces') if not province_map.is_water_province(province_id))
    groups[k] = str(state['id'])
    
    history = state['history'].at_time(date)
    controller = history['controller'] or history['owner']
    controller_color = country_colors[controller]

    if controller in history.find_all('add_core_of'):
        color = tuple(x // 4 + 191 for x in controller_color)
        textcolormap[k] = (0, 0, 0)
    else:
        color = tuple(x // 4 for x in controller_color)
        textcolormap[k] = (255, 255, 255)

    # color the province
    for province_id in state.find_all('provinces'):
        if not province_map.is_water_province(province_id):
            colormap[province_id] = color

out = province_map.generate_image(colormap, default_land_color=(255, 255, 255), edge_color=(127, 127, 127), edge_groups = groups.keys())
# out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
province_map.overlay_text(out, groups, colormap = textcolormap, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/add_core_of_map.png')
#pyradox.image.save_using_palette(out, 'out/province__id_map.png')
