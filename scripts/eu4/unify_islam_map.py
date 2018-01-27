import _initpath
import os
import pyradox.config
import pyradox
import pyradox.worldmap

colormap = {}
tree = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('EU4'), 'decisions', 'Muslim.txt'))
unify_requirements = tree['country_decisions']['unify_islam']['allow']
for province_id in unify_requirements.find_all('owns_or_vassal_of'):
    colormap[province_id] = (0, 127, 0)
        
province_map = pyradox.worldmap.ProvinceMap()
out = province_map.generate_image(colormap)
out.save('out/unify_islam_map.png')
