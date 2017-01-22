import _initpath
import csv
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.worldmap

from PIL import Image

#date = pyradox.primitive.Date('1936.1.1')
date = pyradox.primitive.Date('1939.8.14')

vpImages = pyradox.image.splitStrip(Image.open('in/onmap_victorypoints_strip.png'), subwidth = 29)
capitalIcon = vpImages[4]
majorIcon = vpImages[9]
minorIcon = vpImages[14]

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
     

# find all capitals and country colors

# stateID -> [tag]
capitalStates = {}
countryColors = {}

countryColorFile = pyradox.txt.parseFile(os.path.join(pyradox.config.getBasedir('HoI4'), 'common', 'countries', 'colors.txt'))

for filename, country in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'countries')):
    tag = computeCountryTag(filename)
    if tag in countryColorFile:
        countryColors[tag] = computeColor([x for x in countryColorFile[tag].findAll('color')])
    else:
        print('HACK FOR %s' % tag)
        countryColors[tag] = (165, 102, 152)
    print(tag, countryColors[tag])
    if country['capital'] not in capitalStates: capitalStates[country['capital']] = []
    capitalStates[country['capital']].append(tag)

# Load states.
states = pyradox.txt.parseMerge(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'states'))
provinceMap = pyradox.worldmap.ProvinceMap()

colormap = {}
iconmap = {}
textmap = {}
iconoffsetmap = {}
for state in states.values():
    history = state['history'].atDate(date)
    controller = history['controller'] or history['owner']
    controllerColor = countryColors[controller]

    # color the province
    for provinceID in state.findAll('provinces'):
        if not provinceMap.isWaterProvince(provinceID):
            colormap[provinceID] = controllerColor

    needCapital = (state['id'] in capitalStates and controller in capitalStates[state['id']])

    if state['id'] in capitalStates and not controller in capitalStates[state['id']]:
        print("Country %s overriding %s" % (controller, capitalStates[state['id']]))
        
    for provinceID, vp in history.findAll('victory_points', tupleLength = 2):
        # write number of vps
        textmap[provinceID] = str(vp)

        # set icon
        if needCapital:
            iconmap[provinceID] = capitalIcon
            iconoffsetmap[provinceID] = (0, -2)
            needCapital = False
        elif vp > 5:
            iconmap[provinceID] = majorIcon
        else:
            iconmap[provinceID] = minorIcon

    # backup capital
    if needCapital:
        capitalProvinceID = state['provinces'][0]
        iconmap[capitalProvinceID] = capitalIcon
        iconoffsetmap[capitalProvinceID] = (0, -2)
        textmap[capitalProvinceID] = '0'

out = provinceMap.generateImage(colormap, defaultWaterColor=(32, 32, 63))

pyradox.image.saveUsingPalette(out, 'out/political_map.png')

provinceMap.overlayIcons(out, iconmap, offsetmap = iconoffsetmap)
provinceMap.overlayText(out, textmap, fontfile = "tahoma.ttf", fontsize = 9, antialias = False, defaultFontColor=(0, 255, 0), defaultOffset = (0, -3))

pyradox.image.saveUsingPalette(out, 'out/victory_point_map.png')
