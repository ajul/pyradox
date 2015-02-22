import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.primitive
import pyradox.txt
import pyradox.worldmap
import pyradox.hoi3.province

vanilla_provinces = pyradox.hoi3.province.getProvinces(basedir = pyradox.config.basedirs['HoI3_vanilla'])
tfh_provinces = pyradox.hoi3.province.getProvinces(basedir = pyradox.config.basedirs['HoI3'])
provinceMap = pyradox.worldmap.ProvinceMap(pyradox.config.basedirs['HoI3'], flipY = True)
provinceContents = {
    'infra' : (1, 10, 1),
    'industry' : (1, 10, 1),
    'leadership' : (0.0, 3.0, 0.5),
    'manpower' : (0.0, 20.0, 1.0),
    'energy' : (0.0, 150.0, 10.0),
    'metal' : (0.0, 100.0, 10.0),
    'rare_materials' : (0.0, 30.0, 2.5),
    'crude_oil' : (0.0, 160.0, 10.0),
    'air_base' : (1, 10, 1),
    'naval_base' : (1, 10, 1),
    'anti_air' : (1, 10, 1),
    'points' : (0, 30, 5),
    }

def printLegend(minVal, maxVal, step = 1):
    result = ''
    x = minVal
    while x <= maxVal:
        color = pyradox.image.colormapRedGreen((x - valMin) / valRange)
        bgColorString = '#%02x%02x%02x' % color
        r, g, b = color
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if y >= 255 / 2:
            textColorString = '#000000'
        else:
            textColorString = '#ffffff'
        result += '<span style="color:%s; background-color:%s">%0.2f </span>' % (textColorString, bgColorString, x)
        x += step
    print(result)

for mode in provinceContents:

    valMin, valMax, step = provinceContents[mode]
    valRange = valMax - valMin

    printLegend(valMin, valMax, step)

    colormap = {}
    for provinceID, data in vanilla_provinces.items():
        data = data.atDate(pyradox.primitive.Date('1936.1.1'))
        if mode in data.keys():
            colormap[int(provinceID)] = pyradox.image.colormapRedGreen((data[mode] - valMin) / valRange)
            
    for provinceID, data in tfh_provinces.items():
        data = data.atDate(pyradox.primitive.Date('1936.1.1'))
        if mode in data.keys():
            colormap[int(provinceID)] = pyradox.image.colormapRedGreen((data[mode] - valMin) / valRange)

    out = provinceMap.generateImage(colormap)
    out.save('out/%s_map.png' % mode)
