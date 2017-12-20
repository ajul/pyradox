import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.worldmap
        
province_map = pyradox.worldmap.ProvinceMap(pyradox.config.basedirs['HoI3'], flip_y = True)

colormap = {}

out = province_map.generate_image(colormap, default_land_color=(255, 255, 255))
pyradox.image.save_using_palette(out, 'out/blank_map.png')

