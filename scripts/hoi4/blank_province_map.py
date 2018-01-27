import hoi4
import os
import re
import collections


import pyradox

        
province_map = pyradox.worldmap.ProvinceMap(basedir = pyradox.get_game_directory('HoI4'))

out = province_map.generate_image({}, default_land_color=(255, 255, 255))
pyradox.image.save_using_palette(out, 'out/blank_province_map.png')
