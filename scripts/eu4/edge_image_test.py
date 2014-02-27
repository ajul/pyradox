import _initpath
import os
import re
import collections
import pyradox.txt
import pyradox.worldmap

basedir = r'D:\Steam\steamapps\common\Europa Universalis IV'
        
provinceMap = pyradox.worldmap.ProvinceMap(basedir)
pyradox.worldmap.generateEdgeImage(provinceMap.provinceImage, scale=1.0, edgeWidth = 1).save('out/edge_image.png')

