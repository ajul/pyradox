import _initpath
import os
import re
import math
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.primitive
import pyradox.worldmap

import pyradox.eu4.province

import scipy.stats

provinces = pyradox.eu4.province.getProvinces()

def provinceBaseTax(province):
    if 'base_tax' in province and province['base_tax'] > 0:
        return province['base_tax']
    else:
        return None

def provinceManpower(province):
    if 'manpower' in province and province['manpower'] > 0:
        return province['manpower']
    else:
        return None

def provinceCost(province):
    cost = 0
    if 'base_tax' in province:
        if 'trade_goods' in province and province['trade_goods'] == 'gold':
            cost += 4 * province['base_tax']
        else:
            cost += province['base_tax']
            
    if 'manpower' in province:
        cost += province['manpower']

    if 'extra_cost' in province:
        cost += province['extra_cost']

    if cost > 0:
        return math.floor(cost)
    else:
        return None

def nativePopulation(province):
    if 'native_size' in province:
        return province['native_size'] / 10.0
    else:
        return None

rankMethod = 'dense'

def generateMap(provinceFunction, filename, forceMin = None):
    numberMap = {int(re.match('\d+', filename).group(0)) : provinceFunction(province.atDate(pyradox.primitive.Date('1444.11.11')))
                 for filename, province in provinces.items()
                 if provinceFunction(province) is not None}
    
    if forceMin is None:
        forceMin = min(numberMap.values())

    effectiveNumbers = [max(x, forceMin) for x in numberMap.values()]
        
    ranks = scipy.stats.rankdata(effectiveNumbers, method = rankMethod)
    minRank = min(ranks)
    maxRank = max(ranks)
    rangeRank = maxRank - minRank
    colors = {}
    for number, rank in zip(numberMap.values(), ranks):
        if number < forceMin:
            colors[number] = pyradox.image.colormapBlueRed(0.0)
        else:
            colors[number] = pyradox.image.colormapBlueRed((rank - minRank) / rangeRank)
    colorMap = {provinceID : colors[number] for provinceID, number in numberMap.items()}
    textMap = {provinceID : ('%d' % number if number >= 1.0 or number == 0 else '%0.1f' % number) for provinceID, number in numberMap.items()}

    provinceMap = pyradox.worldmap.ProvinceMap()
    image = provinceMap.generateImage(colorMap)
    provinceMap.overlayText(image, textMap, fontfile = "tahoma.ttf", defaultFontColor=(255, 255, 255), fontsize = 9, antialias = False)
    pyradox.image.saveUsingPalette(image, filename)
        
generateMap(provinceBaseTax, 'out/base_tax_map.png', forceMin = 1.0)
generateMap(provinceManpower, 'out/base_manpower_map.png', forceMin = 1.0)
generateMap(provinceCost, 'out/custom_nation_cost_map.png', forceMin = 2.0)
generateMap(nativePopulation, 'out/native_population_map.png')



