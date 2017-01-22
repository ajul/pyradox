import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.worldmap
        
provinceMap = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.getBasedir('HoI4'))

out = provinceMap.generateImage({}, defaultLandColor=(255, 255, 255))
pyradox.image.saveUsingPalette(out, 'out/blank_province_map.png')
