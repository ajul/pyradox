import _initpath
import os
import re
import collections

import pyradox
import pyradox.worldmap

color_defs = collections.OrderedDict([
    ('default', (127, 127, 127)),
    ('tropical' , (255, 63, 63)),       # light red
    ('arid' , (255, 255, 127)),         # light yellow
    ('arctic' , (127, 127, 255)),       # light blue

    #('default', (0, 63, 0)),            #
    #('mild_winter', (0, 191, 0)),       # green
    #('normal_winter', (63, 255, 63)),   # light green
    #('severe_winter', (191, 255, 191)), # pale green
    ])

legend = ''
for name, color in color_defs.items():
    bg_color_string = '#%02x%02x%02x' % color
    r, g, b = color
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if y >= 255 / 2:
        text_color_string = '#000000'
    else:
        text_color_string = '#ffffff'
    legend += '<span style="color:%s; background-color:%s">%s </span>' % (text_color_string, bg_color_string, name)

print(legend)

climate_map = {}
for climate, provinces in pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('EU4'), 'map', 'climate.txt'), verbose=False).items():
    for province_id in provinces:
        if climate in color_defs.keys():
            climate_map[province_id] = climate

colormap = {}
for filename, data in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('EU4'), 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    province_id = int(m.group(0))
    if 'base_tax' not in data: continue # skip wastelands
    if province_id in climate_map:
        colormap[province_id] = color_defs[climate_map[province_id]]
    else:
        colormap[province_id] = color_defs['default']
        
province_map = pyradox.worldmap.ProvinceMap()
out = province_map.generate_image(colormap)
out.save('out/climate_map.png')


