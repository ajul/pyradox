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
# import province_costs

provinces = pyradox.eu4.province.getProvinces()

def provinceBaseTax(provinceID, province):
    if 'base_tax' in province and province['base_tax'] > 0:
        return province['base_tax']
    else:
        return None

def provinceBaseProduction(provinceID, province):
    if 'base_production' in province and province['base_production'] > 0:
        return province['base_production']
    else:
        return None

def provinceBaseManpower(provinceID, province):
    if 'base_manpower' in province and province['base_manpower'] > 0:
        return province['base_manpower']
    else:
        return None

def provinceBaseDevelopment(provinceID, province):
    result = (
        (provinceBaseTax(provinceID, province) or 0) +
        (provinceBaseProduction(provinceID, province) or 0) +
        (provinceBaseManpower(provinceID, province) or 0))
    if result > 0:
        return result
    else:
        return None
    
def nativePopulation(provinceID, province):
    if 'native_size' in province:
        return province['native_size'] / 10.0
    else:
        return None

def nativeAggressiveness(provinceID, province):
    if 'native_size' in province:
        return province['native_hostileness'] or 0
    else:
        return None

rankMethod = 'dense'

def generateMap(provinceFunction, filename, forceMin = None):
    numberMap = {int(re.match('\d+', filename).group(0)) :
                 provinceFunction(int(re.match('\d+', filename).group(0)), province.atDate(pyradox.primitive.Date('1444.11.11')))
                 for filename, province in provinces.items()
                 if provinceFunction(int(re.match('\d+', filename).group(0)), province) is not None}
    
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
    textMap = {provinceID : ('%d' % round(number)) for provinceID, number in numberMap.items()}

    provinceMap = pyradox.worldmap.ProvinceMap()
    image = provinceMap.generateImage(colorMap)
    provinceMap.overlayText(image, textMap, fontfile = "tahoma.ttf", defaultFontColor=(255, 255, 255), fontsize = 9, antialias = False)
    pyradox.image.saveUsingPalette(image, filename)
        
generateMap(provinceBaseTax, 'out/base_tax_map.png', forceMin = 1.0)
generateMap(provinceBaseProduction, 'out/base_production_map.png', forceMin = 1.0)
generateMap(provinceBaseManpower, 'out/base_manpower_map.png', forceMin = 1.0)
generateMap(provinceBaseDevelopment, 'out/base_development_map.png', forceMin = 3.0)
# generateMap(province_costs.provinceCost, 'out/custom_nation_cost_map.png', forceMin = 1.0)
# generateMap(nativePopulation, 'out/native_population_map.png')
# generateMap(nativeAggressiveness, 'out/native_aggressiveness_map.png')



