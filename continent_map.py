import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
from PIL import Image

drawIDs = True

colorDefs = collections.OrderedDict([
    ('europe', (127, 255, 255)),        #cyan
    ('asia', (255, 255, 127)),          #yellow
    ('africa', (127, 127, 255)),        #blue
    ('north_america', (255, 127, 127)), #red
    ('south_america', (127, 255, 127)), #green
    ('oceania', (255, 127, 255)),         #magenta
    ('default', (127, 127, 127)),       #gray
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

continentMap = {}
for continent, provinces in pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'map', 'continent.txt'), verbose=False).items():
    for provinceID in provinces:
        if provinceID in continentMap:
            print('Duplicate continent for province %d' % provinceID)
        else:
            continentMap[provinceID] = continent

colormap = {}
for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    provinceID = int(m.group(0))
    if 'base_tax' not in data: continue # skip wastelands
    if provinceID in continentMap:
        colormap[provinceID] = colorDefs[continentMap[provinceID]]
    else:
        print('Missing continent for province %d' % provinceID)
        colormap[provinceID] = colorDefs['default']
        
provinceMap = pyradox.worldmap.ProvinceMap()
out = provinceMap.generateImage(colormap)

if drawIDs:
    out = out.resize((out.size[0] * 2, out.size[1] * 2), Image.ANTIALIAS)
    textmap = {}
    colormap = {}
    for provinceID in provinceMap.positions.keys():
        textmap[provinceID] = '%d' % provinceID
        if provinceMap.isWaterProvince(provinceID):
            colormap[provinceID] = (0, 0, 127)
        else:
            colormap[provinceID] = (0, 0, 0)

    provinceMap.overlayText(out, textmap, colormap = colormap)
    out.save('out/continent_ID_map.png')
else:
    out.save('out/continent_map.png')




