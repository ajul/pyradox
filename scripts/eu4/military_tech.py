import _initpath
import os
import pyradox.config
import pyradox.format
import pyradox.primitive
import pyradox.txt
import pyradox.yml

# Parse the military tech file.
tree = pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'technologies', 'mil.txt'))

# Base statistics.
stats = {
    'land_morale' : 0.0,
    'military_tactics' : 0.5,
    'infantry_fire' : 0.0,
    'infantry_shock' : 0.0,
    'cavalry_fire' : 0.0,
    'cavalry_shock' : 0.0,
    'artillery_fire' : 0.0,
    'artillery_shock' : 0.0,
    'combat_width' : 15,
    'supply_limit' : 0.0,
    }

w = '{| class = "wikitable"\n'
w += '! rowspan = "2" | Tech level !! rowspan = "2" | Year !! rowspan = "2" | Morale !! rowspan = "2" | Military<br/>Tactics '
w += '!! colspan = "2" | Infantry !! colspan = "2" | Cavalry !! colspan = "2" | Artillery '
w += '!! rowspan = "2" | Combat<br/>Width !! rowspan = "2" | Supply<br/>Limit '
w += '\n|-\n'
w += '! Fire !! Shock !! Fire !! Shock !! Fire !! Shock\n'

# Find all techs in the file, update values, and output.
for level, tech in enumerate(tree.findAll('technology')):
    stats['level'] = level
    for key, value in tech.items():
        if key == 'year':
            stats['year'] = value
        elif key in stats.keys():
            stats[key] += value

    stats['supply_limit%'] = stats['supply_limit'] * 100.0
    w += '|-\n'
    w += '| %(level)s || %(year)d || %(land_morale)0.2f || %(military_tactics)0.2f ' % stats
    w += '|| %(infantry_fire)0.2f || %(infantry_shock)0.2f ' % stats
    w += '|| %(cavalry_fire)0.2f || %(cavalry_shock)0.2f ' % stats
    w += '|| %(artillery_fire)0.2f || %(artillery_shock)0.2f ' % stats
    w += '|| %(combat_width)d || %(supply_limit%)+0.1f%% ' % stats
    w += '\n'

w += '|}\n'

print(w)


