import _initpath

import pyradox.csv
import os

weapon_path = os.path.join(
    pyradox.get_game_directory('Stellaris'),
    'common',
    'component_templates',
    'weapon_components.csv')

data = pyradox.csv.parse_file(weapon_path)

print(data.to_wiki())
f = open('out/weapons.csv', 'w')
f.write(data.to_csv())
f.close()
