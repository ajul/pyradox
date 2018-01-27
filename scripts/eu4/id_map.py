import _initpath
import os
import re
import collections
import pyradox.config
import pyradox
import pyradox.worldmap
import pyradox.image
from PIL import Image

# Load the province map using the default location set in pyradox.config.
province_map = pyradox.worldmap.ProvinceMap()

colormap = {}
for filename, data in pyradox.txt.parse_dir(os.path.join(pyradox.config.get_game_directory('EU4'), 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    province_id = int(m.group(0))
    if ('base_tax' in data and data['base_tax'] > 0):
        colormap[province_id] = (150, 150, 150)

# Create a blank map and scale it up 2x.
out = province_map.generate_image(colormap, default_land_color=(97, 97, 97), default_water_color=(68, 107, 163), edge_color=(255, 255, 255))
out = out.resize((out.size[0] * 2, out.size[1] * 2), Image.NEAREST)

# Create the map labels.
textmap = {}
colormap = {}
for province_id in province_map.positions.keys():
    textmap[province_id] = '%d' % province_id
    if province_map.is_water_province(province_id):
        colormap[province_id] = (0, 0, 0)
    else:
        colormap[province_id] = (0, 0, 0)

province_map.overlay_text(out, textmap, colormap = colormap, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/province__id_map.png')
#pyradox.image.save_using_palette(out, 'out/province__id_map.png')
