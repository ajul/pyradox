import _initpath
import os
import re
import collections
import province_costs
import pyradox.config
import pyradox.txt
import pyradox.worldmap
from PIL import Image

draw_id_s = False

color_defs = collections.OrderedDict([
    ('europe', (127, 255, 255)),        #cyan
    ('asia', (255, 255, 127)),          #yellow
    ('africa', (127, 127, 255)),        #blue
    ('north_america', (255, 127, 127)), #red
    ('south_america', (127, 255, 127)), #green
    ('oceania', (255, 127, 255)),         #magenta
    ('default', (127, 127, 127)),       #gray
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

continent_map = {}
for continent, provinces in pyradox.txt.parse_file(os.path.join(pyradox.config.get_basedir('EU4'), 'map', 'continent.txt'), verbose=False).items():
    for province_id in provinces:
        if province_id in continent_map:
            print('Duplicate continent for province %d' % province_id)
        else:
            continent_map[province_id] = continent

continent_province_count = {}
continent_base_tax = {}
continent_production = {}
continent_manpower = {}
continent_cost = {}
for continent in color_defs.keys():
    continent_province_count[continent] = 0
    continent_base_tax[continent] = 0
    continent_production[continent] = 0
    continent_manpower[continent] = 0
    
    continent_cost[continent] = 0
    
colormap = {}
for filename, data in pyradox.txt.parse_dir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    province_id = int(m.group(0))
    if 'base_tax' not in data: continue # skip wastelands
    if province_id in continent_map:
        continent = continent_map[province_id]
        continent_province_count[continent] += 1
        continent_base_tax[continent] += data['base_tax']
        continent_production[continent] += data['base_production']
        continent_manpower[continent] += data['base_manpower']
        continent_cost[continent] += province_costs.province_cost(province_id, data)
        colormap[province_id] = color_defs[continent]
    else:
        print('Missing continent for province %d' % province_id)
        colormap[province_id] = color_defs['default']

print(continent_province_count)
print(continent_base_tax)
print(continent_production)
print(continent_manpower)
print(continent_cost)

province_map = pyradox.worldmap.ProvinceMap()
out = province_map.generate_image(colormap)

if draw_id_s:
    out = out.resize((out.size[0] * 2, out.size[1] * 2), Image.ANTIALIAS)
    textmap = {}
    colormap = {}
    for province_id in province_map.positions.keys():
        textmap[province_id] = '%d' % province_id
        if province_map.is_water_province(province_id):
            colormap[province_id] = (0, 0, 127)
        else:
            colormap[province_id] = (0, 0, 0)

    province_map.overlay_text(out, textmap, colormap = colormap)
    out.save('out/continent__id_map.png')
else:
    out.save('out/continent_map.png')




