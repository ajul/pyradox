import initpath
import os
import re
import collections
from PIL import Image
import pyradox.config
import pyradox.txt
import pyradox.worldmap

terrainBMP = os.path.join(pyradox.config.basedirs['EU4'], 'map', 'terrain.bmp')
terrainMap = Image.open(terrainBMP).convert('RGB')

provinceMap = pyradox.worldmap.ProvinceMap()
provinceMap.overlayEdgesOnImage(terrainMap)
terrainMap.save('out/terrain_map.png')

