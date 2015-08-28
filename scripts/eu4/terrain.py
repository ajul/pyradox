import _initpath
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import os
from PIL import Image

provinceMap = pyradox.worldmap.ProvinceMap()
terrainMapImage = Image.open('in/terrain.png')
terrainTXT = pyradox.txt.parseFile(os.path.join(os.path.join(pyradox.config.basedirs['EU4'], 'map', 'terrain.txt')))

terrainByColor = {}

for terrainName, terrain in terrainTXT['categories'].items():
    if 'color' in terrain:
        color = tuple(terrain['color'])
        terrainByColor[color] = (terrainName, terrain)

def getProvinceTerrain(provinceID):
    position = provinceMap.positions[provinceID]
    color = terrainMapImage.getpixel(position)
    return terrainByColor[tuple(color)]
