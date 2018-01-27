import _initpath
import os
import re
import collections

import pyradox



from PIL import Image
import load.province

resource_image_dir = 'in/strategic_resource/'

province_map = pyradox.worldmap.ProvinceMap(basedir = pyradox.get_game_directory('HoI3'), flip_y = True)

resource_images = {}
for filename in os.listdir(resource_image_dir):
    if os.path.isfile(os.path.join(resource_image_dir, filename)):
        m = re.match(r'strategic_resource_(.*).png', filename)
        if m is None: continue
        resource_images[m.group(1)] = Image.open(os.path.join(resource_image_dir, filename))

vanilla_provinces = load.province.get_provinces(basedir = pyradox.get_game_directory('HoI3_vanilla'))
tfh_provinces = load.province.get_provinces(basedir = pyradox.get_game_directory('HoI3'))

iconmap = {}

for province_id, data in vanilla_provinces.items():
    if 'strategic_resource' in data.keys(): iconmap[int(province_id)] = resource_images[data['strategic_resource']]
        
for province_id, data in tfh_provinces.items():
    if 'strategic_resource' in data.keys(): iconmap[int(province_id)] = resource_images[data['strategic_resource']]
            

out_map_image = province_map.generate_image({})
province_map.overlay_icons(out_map_image, iconmap)
out_map_image.save('out/strategic_resource_map.png')
