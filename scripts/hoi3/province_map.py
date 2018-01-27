import _initpath
import os
import re
import collections

import pyradox.image

import pyradox
import pyradox.worldmap
import load.province

vanilla_provinces = load.province.get_provinces(basedir = pyradox.get_game_directory('HoI3_vanilla'))
tfh_provinces = load.province.get_provinces(basedir = pyradox.get_game_directory('HoI3'))
province_map = pyradox.worldmap.ProvinceMap(pyradox.get_game_directory('HoI3'), flip_y = True)
province_contents = {
    'infra' : (1, 10, 1),
    'industry' : (1, 10, 1),
    'leadership' : (0.0, 3.0, 0.5),
    'manpower' : (0.0, 20.0, 1.0),
    'energy' : (0.0, 150.0, 10.0),
    'metal' : (0.0, 100.0, 10.0),
    'rare_materials' : (0.0, 30.0, 2.5),
    'crude_oil' : (0.0, 160.0, 10.0),
    'air_base' : (1, 10, 1),
    'naval_base' : (1, 10, 1),
    'anti_air' : (1, 10, 1),
    'points' : (0, 30, 5),
    }

def print_legend(min_val, max_val, step = 1):
    result = ''
    x = min_val
    while x <= max_val:
        color = pyradox.image.colormap_red_green((x - val_min) / val_range)
        bg_color_string = '#%02x%02x%02x' % color
        r, g, b = color
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if y >= 255 / 2:
            text_color_string = '#000000'
        else:
            text_color_string = '#ffffff'
        result += '<span style="color:%s; background-color:%s">%0.2f </span>' % (text_color_string, bg_color_string, x)
        x += step
    print(result)

for mode in province_contents:

    val_min, val_max, step = province_contents[mode]
    val_range = val_max - val_min

    print_legend(val_min, val_max, step)

    colormap = {}
    for province_id, data in vanilla_provinces.items():
        data = data.at_date(pyradox.Date('1936.1.1'))
        if mode in data.keys():
            colormap[int(province_id)] = pyradox.image.colormap_red_green((data[mode] - val_min) / val_range)
            
    for province_id, data in tfh_provinces.items():
        data = data.at_date(pyradox.Date('1936.1.1'))
        if mode in data.keys():
            colormap[int(province_id)] = pyradox.image.colormap_red_green((data[mode] - val_min) / val_range)

    out = province_map.generate_image(colormap)
    out.save('out/%s_map.png' % mode)
