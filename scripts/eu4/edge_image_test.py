import _initpath
import os
import re
import collections
import pyradox


basedir = r'D:\Steam\steamapps\common\Europa Universalis IV'
        
province_map = pyradox.worldmap.ProvinceMap(basedir)
pyradox.worldmap.generate_edge_image(province_map.province_image, scale=1.0, edge_width = 1).save('out/edge_image.png')

