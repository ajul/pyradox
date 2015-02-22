import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.primitive
import pyradox.image
from PIL import Image
import pyradox.hoi3.province

resourceImageDir = 'in/strategic_resource/'

provinceMap = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.basedirs['HoI3'], flipY = True)

resourceImages = {}
for filename in os.listdir(resourceImageDir):
    if os.path.isfile(os.path.join(resourceImageDir, filename)):
        m = re.match(r'strategic_resource_(.*).png', filename)
        if m is None: continue
        resourceImages[m.group(1)] = Image.open(os.path.join(resourceImageDir, filename))

vanilla_provinces = pyradox.hoi3.province.getProvinces(basedir = pyradox.config.basedirs['HoI3_vanilla'])
tfh_provinces = pyradox.hoi3.province.getProvinces(basedir = pyradox.config.basedirs['HoI3'])

iconmap = {}

for provinceID, data in vanilla_provinces.items():
    if 'strategic_resource' in data.keys(): iconmap[int(provinceID)] = resourceImages[data['strategic_resource']]
        
for provinceID, data in tfh_provinces.items():
    if 'strategic_resource' in data.keys(): iconmap[int(provinceID)] = resourceImages[data['strategic_resource']]
            

outMapImage = provinceMap.generateImage({})
provinceMap.overlayIcons(outMapImage, iconmap)
outMapImage.save('out/strategic_resource_map.png')
