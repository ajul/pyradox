import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.primitive
import pyradox.image
from PIL import Image

startDate = pyradox.primitive.Date('1444.11.11')

# get trade goods
resourceImages = pyradox.image.splitStrip(Image.open('in/resources.png'))

tradeGoodIcons = {}
tree = pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'tradegoods', '00_tradegoods.txt'))
for idx, tradeGood in enumerate(tree.keys()):
    tradeGoodIcons[tradeGood] = resourceImages[idx]
    resourceImages[idx].save('out/tradegoods/trade_good_%s.png' % tradeGood)

colormap = {}
iconmap = {}

for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    provinceID = int(m.group(0))
    startData = data.atDate(startDate)
    # endData = data.atDate(True)
    if 'base_tax' in data:
        if 'owner' in startData:
            colormap[provinceID] = (191, 191, 191)
        else:
            colormap[provinceID] = (127, 127, 127)
        tradeGood = 'unknown'
        for currGood in data.findWalk('trade_goods'):
            if currGood != 'unknown':
                tradeGood = currGood
        iconmap[provinceID] = tradeGoodIcons[tradeGood]
            
        
provinceMap = pyradox.worldmap.ProvinceMap()
baseMap = provinceMap.generateImage(colormap)
maxSizeMap = baseMap.resize((baseMap.size[0] * 4, baseMap.size[1] * 4), Image.ANTIALIAS)
provinceMap.overlayIcons(maxSizeMap, iconmap)
# maxSizeMap.save('out/trade_good_icon_map_max.png')

doubleSizeMap = maxSizeMap.resize((baseMap.size[0] * 2, baseMap.size[1] * 2), Image.ANTIALIAS)
doubleSizeMap.save('out/trade_good_icon_map_double.png', optimize = True)

regularSizeMap = maxSizeMap.resize((baseMap.size[0], baseMap.size[1]), Image.ANTIALIAS)
regularSizeMap.save('out/trade_good_icon_map.png', optimize = True)
