import _initpath
import os
import re
import collections
from PIL import Image
import pyradox.config
import pyradox
import pyradox.worldmap

base_bmp = os.path.join(pyradox.get_game_directory('EU4'), 'map', 'rivers.bmp')
rivers_map = Image.open(base_bmp).convert('RGB')

province_map = pyradox.worldmap.ProvinceMap()
province_map.overlay_edges(rivers_map)
rivers_map.save('out/rivers_map.png')


