import _initpath
import os
import re
import collections
from PIL import Image
import pyradox.config
import pyradox.txt
import pyradox.worldmap

baseBMP = os.path.join(pyradox.config.basedirs['EU4'], 'map', 'rivers.bmp')
riversMap = Image.open(baseBMP).convert('RGB')

provinceMap = pyradox.worldmap.ProvinceMap()
provinceMap.overlayEdges(riversMap)
riversMap.save('out/rivers_map.png')


