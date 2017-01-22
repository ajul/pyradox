import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.image
from PIL import Image

def computeCountryTag(filename):
    m = re.match('.*([A-Z]{3})\s*-.*\.txt$', filename)
    return m.group(1)

def computeColor(values):
    if isinstance(values[0], int):
        # rgb
        r = values[0]
        g = values[1]
        b = values[2]
        return (r, g, b)
    else:
        # hsv
        return pyradox.image.HSVtoRGB(values)
     

date = pyradox.primitive.Date('1936.1.1')
scale = 2.0

# stateID -> [tag]
capitalStates = {}
countryColors = {}

countryColorFile = pyradox.txt.parseFile(os.path.join(pyradox.config.getBasedir('HoI4'), 'common', 'countries', 'colors.txt'))

for filename, country in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'countries')):
    tag = computeCountryTag(filename)
    if tag in countryColorFile:
        countryColors[tag] = computeColor(tuple(countryColorFile[tag].findAll('color')))
    else:
        print('HACK FOR %s' % tag)
        countryColors[tag] = (165, 102, 152)
    print(tag, countryColors[tag])
    if country['capital'] not in capitalStates: capitalStates[country['capital']] = []
    capitalStates[country['capital']].append(tag)

# Load states.
states = pyradox.txt.parseMerge(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'states'))
provinceMap = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.getBasedir('HoI4'))

# provinces -> state id
colormap = {}
textcolormap = {}
groups = {}

for state in states.values():
    k = tuple(provinceID for provinceID in state.findAll('provinces') if not provinceMap.isWaterProvince(provinceID))
    groups[k] = str(state['id'])
    
    history = state['history'].atDate(date)
    controller = history['controller'] or history['owner']
    controllerColor = countryColors[controller]

    if controller in history.findAll('add_core_of'):
        color = tuple(x // 4 + 191 for x in controllerColor)
        textcolormap[k] = (0, 0, 0)
    else:
        color = tuple(x // 4 for x in controllerColor)
        textcolormap[k] = (255, 255, 255)

    # color the province
    for provinceID in state.findAll('provinces'):
        if not provinceMap.isWaterProvince(provinceID):
            colormap[provinceID] = color

out = provinceMap.generateImage(colormap, defaultLandColor=(255, 255, 255), edgeColor=(127, 127, 127), edgeGroups = groups.keys())
# out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)

# unfortunately lakes don't have unitstacks.txt
provinceMap.overlayText(out, groups, colormap = textcolormap, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
out.save('out/add_core_of_map.png')
#pyradox.image.saveUsingPalette(out, 'out/province_ID_map.png')
