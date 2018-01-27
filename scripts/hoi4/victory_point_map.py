import hoi4
import csv
import os
import re
import collections


import pyradox


from PIL import Image

#date = pyradox.Date('1936.1.1')
date = pyradox.Date('1939.8.14')

vp_images = pyradox.image.split_strip(Image.open('in/onmap_victorypoints_strip.png'), subwidth = 29)
capital_icon = vp_images[4]
major_icon = vp_images[9]
minor_icon = vp_images[14]

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
     

# find all capitals and country colors

# state_id -> [tag]
capital_states = {}
country_colors = {}

country_color_file = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('HoI4'), 'common', 'countries', 'colors.txt'))

for filename, country in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'countries')):
    tag = compute_country_tag(filename)
    if tag in country_color_file:
        country_colors[tag] = compute_color([x for x in country_color_file[tag].find_all('color')])
    else:
        print('HACK FOR %s' % tag)
        country_colors[tag] = (165, 102, 152)
    print(tag, country_colors[tag])
    if country['capital'] not in capital_states: capital_states[country['capital']] = []
    capital_states[country['capital']].append(tag)

# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'states'))
province_map = pyradox.worldmap.ProvinceMap()

colormap = {}
iconmap = {}
textmap = {}
iconoffsetmap = {}
for state in states.values():
    history = state['history'].at_time(date)
    controller = history['controller'] or history['owner']
    controller_color = country_colors[controller]

    # color the province
    for province_id in state.find_all('provinces'):
        if not province_map.is_water_province(province_id):
            colormap[province_id] = controller_color

    need_capital = (state['id'] in capital_states and controller in capital_states[state['id']])

    if state['id'] in capital_states and not controller in capital_states[state['id']]:
        print("Country %s overriding %s" % (controller, capital_states[state['id']]))
        
    for province_id, vp in history.find_all('victory_points', tuple_length = 2):
        # write number of vps
        textmap[province_id] = str(vp)

        # set icon
        if need_capital:
            iconmap[province_id] = capital_icon
            iconoffsetmap[province_id] = (0, -2)
            need_capital = False
        elif vp > 5:
            iconmap[province_id] = major_icon
        else:
            iconmap[province_id] = minor_icon

    # backup capital
    if need_capital:
        capital_province_id = state['provinces'][0]
        iconmap[capital_province_id] = capital_icon
        iconoffsetmap[capital_province_id] = (0, -2)
        textmap[capital_province_id] = '0'

out = province_map.generate_image(colormap, default_water_color=(32, 32, 63))

pyradox.image.save_using_palette(out, 'out/political_map.png')

province_map.overlay_icons(out, iconmap, offsetmap = iconoffsetmap)
province_map.overlay_text(out, textmap, fontfile = "tahoma.ttf", fontsize = 9, antialias = False, default_font_color=(0, 255, 0), default_offset = (0, -3))

pyradox.image.save_using_palette(out, 'out/victory_point_map.png')
