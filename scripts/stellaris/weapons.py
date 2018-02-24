import _initpath
import pyradox
import os

weapon_path = os.path.join(
    pyradox.get_game_directory('Stellaris'),
    'common',
    'component_templates',
    'weapon_components.csv')

data = pyradox.csv.parse_file(weapon_path)

f = open('out/weapons.wiki', 'w')
f.write(pyradox.filetype.table.make_table(data, 'wiki'))
f.close()
