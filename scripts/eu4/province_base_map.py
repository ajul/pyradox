import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.primitive
import pyradox.worldmap

maxBaseTax = 15
minBaseTax = 1.0
maxManpower = 8
minManpower = 0.5
gamma = 1.0 # give more contrast to lower numbers

def baseTaxColor(x):
    # return (int(x * 255.0 / maxBaseTax), int(x * 255.0 / maxBaseTax), 0)
    return pyradox.image.colormapBlueRed(pow(max(x - minBaseTax, 0) / (maxBaseTax - minBaseTax), gamma))

def manpowerColor(x):
    # return (int(x * 255.0 / maxManpower), 0, 0)
    return pyradox.image.colormapBlueRed(pow(max(x - minManpower, 0) / (maxManpower - minManpower), gamma))

legendBaseTax = ''
for x in range(1, maxBaseTax + 1):
    color = baseTaxColor(x)
    bgColorString = '#%02x%02x%02x' % color
    r, g, b = color
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if y >= 255 / 2:
        textColorString = '#000000'
    else:
        textColorString = '#ffffff'
    legendBaseTax += '<span style="color:%s; background-color:%s">%d </span>' % (textColorString, bgColorString, x)

print(legendBaseTax)

legendManpower = ''
for x in range(0, maxManpower + 1):
    color = manpowerColor(x)
    bgColorString = '#%02x%02x%02x' % color
    r, g, b = color
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if y >= 255 / 2:
        textColorString = '#000000'
    else:
        textColorString = '#ffffff'
    legendManpower += '<span style="color:%s; background-color:%s">%d </span>' % (textColorString, bgColorString, x)

print(legendManpower)

baseTaxColormap = {}
manpowerColormap = {}
for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces'), verbose=False):
    data = data.atDate(pyradox.primitive.Date('1444.11.11'))
    m = re.match('\d+', filename)
    provinceID = int(m.group(0))

    if 'base_tax' in data:
        baseTaxColormap[provinceID] = baseTaxColor(data['base_tax'])
        
    if 'manpower' in data:
        manpowerColormap[provinceID] = manpowerColor(data['manpower'])
    elif 'base_tax' in data:
        manpowerColormap[provinceID] = manpowerColor(0)
        
provinceMap = pyradox.worldmap.ProvinceMap()
pyradox.image.saveUsingPalette(provinceMap.generateImage(baseTaxColormap), 'out/base_tax_map.png')
pyradox.image.saveUsingPalette(provinceMap.generateImage(manpowerColormap), 'out/base_manpower_map.png')



