import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.format
import pyradox
import pyradox.worldmap
import pyradox.yml
from PIL import Image
        
province_map = pyradox.worldmap.ProvinceMap()

region_colors = pyradox.txt.parse_file(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'region_colors', '00_region_colors.txt'))
regions = pyradox.txt.parse_file(os.path.join(pyradox.config.basedirs['EU4'], 'map', 'region.txt'))
trade_good_events = pyradox.txt.parse_file(os.path.join(pyradox.config.basedirs['EU4'], 'events', 'TradeGoods.txt'))

colormap = {}
textmap = {}
for region_index, (region_key, region_provinces) in enumerate(regions.items()):
    if not trade_good_events.contains_value_walk(region_key): continue # filter to regions appearing in trade goods events
    color = tuple(region_colors.value_at(region_index))
    textmap[tuple(region_provinces)] = pyradox.format.human_title(region_key)
    for province_id in region_provinces:
        colormap[province_id] = color
        
out = province_map.generate_image(colormap, edge_color = (255, 255, 255))

province_map.overlay_text(out, textmap, fontsize = 16)
out.save('out/region_trade_good_map.png')
