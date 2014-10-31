import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap

colorDefs = collections.OrderedDict([
    ('default', (127, 127, 127)),
    ('tropical' , (255, 63, 63)),       # light red
    ('arid' , (255, 255, 127)),         # light yellow
    ('arctic' , (127, 127, 255)),       # light blue

    #('default', (0, 63, 0)),            #
    #('mild_winter', (0, 191, 0)),       # green
    #('normal_winter', (63, 255, 63)),   # light green
    #('severe_winter', (191, 255, 191)), # pale green
    ])

legend = ''
for name, color in colorDefs.items():
    bgColorString = '#%02x%02x%02x' % color
    r, g, b = color
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if y >= 255 / 2:
        textColorString = '#000000'
    else:
        textColorString = '#ffffff'
    legend += '<span style="color:%s; background-color:%s">%s </span>' % (textColorString, bgColorString, name)

print(legend)

climateMap = {}
for climate, provinces in pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'map', 'climate.txt'), verbose=False).items():
    for provinceID in provinces:
        if climate in colorDefs.keys():
            climateMap[provinceID] = climate

colormap = {}
for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    provinceID = int(m.group(0))
    if 'base_tax' not in data: continue # skip wastelands
    if provinceID in climateMap:
        colormap[provinceID] = colorDefs[climateMap[provinceID]]
    else:
        colormap[provinceID] = colorDefs['default']
        
provinceMap = pyradox.worldmap.ProvinceMap()
out = provinceMap.generateImage(colormap)
out.save('out/climate_map.png')


