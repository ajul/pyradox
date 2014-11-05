import _initpath
import os
import re
import collections
from PIL import Image
import pyradox.config
import pyradox.txt
import pyradox.worldmap

terrainBMP = os.path.join('in/terrain.png')
terrainMap = Image.open(terrainBMP).convert('RGB')

provinceMap = pyradox.worldmap.ProvinceMap()
provinceMap.overlayEdges(terrainMap)
#terrainMap.save('out/terrain_map.png', optimize = True)
terrainMap.convert("P", dither = Image.NONE, palette = Image.ADAPTIVE).save('out/terrain_map.png', optimize = True)

