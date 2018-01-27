import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.image
import pyradox
import pyradox.worldmap

end_game = False

building_colors = (
    ('tax_assessor', (255, 191, 0)), # gold
    ('embassy', (127, 255, 127)), # green
    ('glorious_monument', (127, 255, 127)), # green
    ('march_building', (127, 255, 127)), # green
    ('grain_depot', (127, 255, 127)), # green
    ('royal_palace', (127, 255, 127)), # green
    ('war_college', (127, 255, 127)), # green
    ('admiralty', (127, 255, 127)), # green
    ('fine_arts_academy', (127, 255, 127)), # green
    ('university', (63, 191, 255)), # blue
    )

colormap = {}
for filename, data in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('EU4'), 'history', 'provinces'), verbose=False):
    if end_game:
        data = data.at_date(True)
    else:
        data = data.at_date('1444.11.11')
    m = re.match('\d+', filename)
    province_id = int(m.group(0))
    color = None
    for building, building_color in building_colors:
        if building in data:
            print(filename, building)
            color = building_color
    if color is not None:
        colormap[province_id] = color
        
province_map = pyradox.worldmap.ProvinceMap()
out = province_map.generate_image(colormap)
pyradox.image.save_using_palette(out, 'out/unique_building_map.png')

