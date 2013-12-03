import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.worldmap

minNativeSize = 0
maxNativeSize = 9000

gamma = 1.0

def colormapMinMax(x, minVal, maxVal):
    return pyradox.image.colormapBlueRed(pow(max(x - minVal, 0) / (maxVal - minVal), gamma))

def printLegend(minVal, maxVal, step = 1):
    result = ''
    for x in range(minVal, maxVal + 1, step):
        color = colormapMinMax(x, minVal, maxVal)
        bgColorString = '#%02x%02x%02x' % color
        r, g, b = color
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if y >= 255 / 2:
            textColorString = '#000000'
        else:
            textColorString = '#ffffff'
        result += '<span style="color:%s; background-color:%s">%d </span>' % (textColorString, bgColorString, x)
    print(result)

printLegend(minNativeSize, maxNativeSize, 1000)

nativeSizeColormap = {}
for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    provinceID = int(m.group(0))

    if 'native_size' in data and 'owner' not in data:
        nativeSizeColormap[provinceID] = colormapMinMax(data['native_size'] * 100, minNativeSize, maxNativeSize)
    elif 'base_tax' in data:
        nativeSizeColormap[provinceID] = (127, 127, 127)
        
provinceMap = pyradox.worldmap.ProvinceMap()
provinceMap.generateImage(nativeSizeColormap).save('out/native_population_map.png')



