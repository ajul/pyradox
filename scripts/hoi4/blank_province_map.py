import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.worldmap
        
province_map = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.get_basedir('HoI4'))

out = province_map.generate_image({}, default_land_color=(255, 255, 255))
pyradox.image.save_using_palette(out, 'out/blank_province_map.png')
