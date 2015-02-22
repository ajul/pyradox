import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.worldmap
        
provinceMap = pyradox.worldmap.ProvinceMap(pyradox.config.basedirs['HoI3'], flipY = True)

colormap = {}

out = provinceMap.generateImage(colormap, defaultLandColor=(255, 255, 255))
pyradox.image.saveUsingPalette(out, 'out/blank_map.png')

