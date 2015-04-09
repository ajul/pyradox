import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.format
import pyradox.image
import pyradox.txt
import pyradox.primitive
import pyradox.yml
import pyradox.worldmap
import province_costs

sources = ['EU4', 'text', 'nw2', 'res_publica', "aow"]

def localized(s):
    return pyradox.yml.getLocalization(s, sources) or pyradox.format.humanTitle(s)


cultureGroups = {}

cultureTree = pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'cultures', '00_cultures.txt'))

for groupName, groupData in cultureTree.items():
    for culture in groupData:
        cultureGroups[culture] = groupName

cultureData = {}
cultureGroupData = {}

for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces'), verbose=False):
    data = data.atDate(pyradox.primitive.Date('1444.11.11'))
    if 'culture' not in data:
        if 'base_tax' in data:
            print('No culture defined in %s.' % filename)
        continue
    if 'owner' not in data:
        continue
    culture = data['culture']
    cultureGroup = cultureGroups[culture]

    culture = localized(culture)
    if culture not in cultureData:
        cultureData[culture] = ['', 0, 0, 0, 0]
    cultureData[culture][0] = localized(cultureGroup)
    cultureGroup = localized(cultureGroup)
    
    if cultureGroup not in cultureGroupData:
        cultureGroupData[cultureGroup] = [0, 0, 0, 0]
    
    cultureData[culture][1] += 1
    cultureGroupData[cultureGroup][0] += 1
    
    if 'base_tax' in data:
        cultureData[culture][2] += data['base_tax']
        cultureGroupData[cultureGroup][1] += data['base_tax']
    if 'manpower' in data:
        cultureData[culture][3] += data['manpower']
        cultureGroupData[cultureGroup][2] += data['manpower']
    cultureData[culture][4] += province_costs.provinceCost(data)
    cultureGroupData[cultureGroup][3] += province_costs.provinceCost(data)

result = ''

result += '{|class = "wikitable sortable mw-collapsible mw-collapsed"\n'
result += '! Culture group !! Province count !! Base tax !! Base manpower !! Cost\n'

for cultureGroup, stats in sorted(cultureGroupData.items()):
    result += '|-\n'
    result += '| %s || %d || %d || %d || %d \n' % tuple([cultureGroup] + stats)

result += '|}\n'

print(result)

result = ''

result += '{|class = "wikitable sortable mw-collapsible mw-collapsed"\n'
result += '! Culture !! Culture group !! Province count !! Base tax !! Base manpower !! Cost\n'

for culture, stats in sorted(cultureData.items()):
    result += '|-\n'
    result += '| %s || %s || %d || %d || %d || %d\n' % tuple([culture] + stats)

result += '|}\n'

print(result)
