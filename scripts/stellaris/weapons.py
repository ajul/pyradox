import _initpath
import pyradox.config
import pyradox.csv
import os

weaponPath = os.path.join(
    pyradox.config.basedirs['Stellaris'],
    'common',
    'component_templates',
    'weapon_components.csv')

data = pyradox.csv.parseFile(weaponPath)

print(data.toWiki())
f = open('out/weapons.csv', 'w')
f.write(data.toCSV())
f.close()
