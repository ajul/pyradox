import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
        
provinceMap = pyradox.worldmap.ProvinceMap()
out = provinceMap.generateImage({}, defaultLandColor=(127, 127, 127))
out.save('out/blank_map.png')


