import _initpath
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

nativeSizeColormap = {}
nativeSizeTextmap = {}
for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('EU4'), 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    provinceID = int(m.group(0))

    if 'native_size' in data:
        nativeSizeColormap[provinceID] = colormapMinMax(data['native_size'] * 100, minNativeSize, maxNativeSize)
        nativeSizeTextmap[provinceID] = '%d' % (data['native_size'] * 100)
    elif 'base_tax' in data:
        nativeSizeColormap[provinceID] = (127, 127, 127)
        
provinceMap = pyradox.worldmap.ProvinceMap()
image = provinceMap.generateImage(nativeSizeColormap)
provinceMap.overlayText(image, nativeSizeTextmap, fontfile = "tahoma.ttf", defaultFontColor=(255, 255, 255), fontsize = 9, antialias = False)
pyradox.image.saveUsingPalette(image, 'out/native_population_map.png')



