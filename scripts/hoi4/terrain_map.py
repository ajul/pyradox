import _initpath
import csv
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox
import pyradox.worldmap

definition_csv = os.path.join(pyradox.config.get_game_directory('HoI4'), 'map', 'definition.csv')
terrains = pyradox.txt.parse_file(os.path.join(pyradox.config.get_game_directory('HoI4'), 'common', 'terrain', '00_terrain.txt'), verbose=False)['categories']

color_override = {
    'desert' : (255, 63, 0), # more red to avoid confusion with plains
    }

symbol_override = {
    'desert' : '⛭',
    'hills' : '△',
    'mountain' : '▲',
    'ocean' : '~',
    'lakes' : '',
    'marsh' : '⚶',
    'forest' : '♧',
    'jungle' : '♣',
    'plains' : '',
    'urban' : '⚑',
    'unknown' : '',
    }

colormap = {}
textmap = {}

with open(definition_csv) as definition_file:
    csv_reader = csv.reader(definition_file, delimiter = ';')
    for row in csv_reader:
        province_id = int(row[0])
        terrain_key = row[6]
        if terrain_key in color_override:
            colormap[province_id] = color_override[terrain_key]
        else:
            colormap[province_id] = tuple(c for c in terrains[terrain_key]['color'])
        textmap[province_id] = symbol_override[terrain_key]

province_map = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.get_game_directory('HoI4'))
out = province_map.generate_image(colormap, default_land_color=(255, 255, 255))
province_map.overlay_text(out, textmap, fontfile = "unifont-8.0.01.ttf", fontsize = 16, antialias = False, default_offset = (4, -2))
pyradox.image.save_using_palette(out, 'out/terrain_map.png')
