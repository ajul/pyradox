import _initpath
import csv
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.worldmap

definitionCSV = os.path.join(pyradox.config.getBasedir('HoI4'), 'map', 'definition.csv')
terrains = pyradox.txt.parseFile(os.path.join(pyradox.config.getBasedir('HoI4'), 'common', 'terrain', '00_terrain.txt'), verbose=False)['categories']

colorOverride = {
    'desert' : (255, 63, 0), # more red to avoid confusion with plains
    }

symbolOverride = {
    'desert' : '⛭',
    'hills' : '△',
    'mountain' : '▲',
    'ocean' : '~',
    'lakes' : '',
    'marsh' : '⚶',
    'forest' : '♧',
    'jungle' : '♣',
    'plains' : '',
    'urban' : '⚑',
    'unknown' : '',
    }

colormap = {}
textmap = {}

with open(definitionCSV) as definitionFile:
    csvReader = csv.reader(definitionFile, delimiter = ';')
    for row in csvReader:
        provinceID = int(row[0])
        terrainKey = row[6]
        if terrainKey in colorOverride:
            colormap[provinceID] = colorOverride[terrainKey]
        else:
            colormap[provinceID] = tuple(c for c in terrains[terrainKey]['color'])
        textmap[provinceID] = symbolOverride[terrainKey]

provinceMap = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.getBasedir('HoI4'))
out = provinceMap.generateImage(colormap, defaultLandColor=(255, 255, 255))
provinceMap.overlayText(out, textmap, fontfile = "unifont-8.0.01.ttf", fontsize = 16, antialias = False, defaultOffset = (4, -2))
pyradox.image.saveUsingPalette(out, 'out/terrain_map.png')
