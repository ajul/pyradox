import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.worldmap

min_native_size = 0
max_native_size = 9000

gamma = 1.0

def colormap_min_max(x, min_val, max_val):
    return pyradox.image.colormap_blue_red(pow(max(x - min_val, 0) / (max_val - min_val), gamma))

native_size_colormap = {}
native_size_textmap = {}
for filename, data in pyradox.txt.parse_dir(os.path.join(pyradox.config.get_game_directory('EU4'), 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    province_id = int(m.group(0))

    if 'native_size' in data:
        native_size_colormap[province_id] = colormap_min_max(data['native_size'] * 100, min_native_size, max_native_size)
        native_size_textmap[province_id] = '%d' % (data['native_size'] * 100)
    elif 'base_tax' in data:
        native_size_colormap[province_id] = (127, 127, 127)
        
province_map = pyradox.worldmap.ProvinceMap()
image = province_map.generate_image(native_size_colormap)
province_map.overlay_text(image, native_size_textmap, default_font_color=(255, 255, 255))
pyradox.image.save_using_palette(image, 'out/native_population_map.png')

native_aggro_colormap = {}
native_aggro_textmap = {}
for filename, data in pyradox.txt.parse_dir(os.path.join(pyradox.config.get_game_directory('EU4'), 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    province_id = int(m.group(0))

    if 'native_hostileness' in data:
        native_aggro_colormap[province_id] = colormap_min_max(data['native_hostileness'], 0, 10)
        native_aggro_textmap[province_id] = '%d' % data['native_hostileness']
    elif 'base_tax' in data:
        native_aggro_colormap[province_id] = (127, 127, 127)
        
province_map = pyradox.worldmap.ProvinceMap()
image = province_map.generate_image(native_size_colormap)
province_map.overlay_text(image, native_size_textmap, default_font_color=(255, 255, 255))
pyradox.image.save_using_palette(image, 'out/native_aggressiveness_map.png')


