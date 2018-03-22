import _initpath

import pyradox
import os

building_path = os.path.join(
    pyradox.get_game_directory('Stellaris'),
    'common',
    'buildings')

data = pyradox.txt.parse_merge(building_path, game = 'Stellaris')

for building_key, building in data.items():
    if not isinstance(building, pyradox.Tree): continue
    can_habitat = True
    if 'potential' in building:
        for planet in building['potential'].find_all('planet'):
            for n in planet.find_all('not'):
                for k, v in n.items():
                    if k == 'is_planet_class' and v == 'pc_habitat': 
                        can_habitat = False
    if can_habitat: print(building_key)
