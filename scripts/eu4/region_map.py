import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.format
import pyradox.txt
import pyradox.worldmap
import pyradox.yml
from PIL import Image
        
provinceMap = pyradox.worldmap.ProvinceMap()

regionColors = pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'region_colors', '00_region_colors.txt'))
regions = pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'map', 'region.txt'))
tradeGoodEvents = pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'events', 'TradeGoods.txt'))

colormap = {}
textmap = {}
for regionIndex, (regionKey, regionProvinces) in enumerate(regions.items()):
    if not tradeGoodEvents.containsValueWalk(regionKey): continue # filter to regions appearing in trade goods events
    color = tuple(regionColors.valueAt(regionIndex))
    textmap[tuple(regionProvinces)] = pyradox.format.humanTitle(regionKey)
    for provinceID in regionProvinces:
        colormap[provinceID] = color
        
out = provinceMap.generateImage(colormap, edgeColor = (255, 255, 255))

provinceMap.overlayText(out, textmap, fontsize = 16)
out.save('out/region_trade_good_map.png')
