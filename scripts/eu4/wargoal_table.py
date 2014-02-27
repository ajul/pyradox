import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.format
import pyradox.image
import pyradox

tree = pyradox.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'wargoal_types', '00_wargoal_types.txt'))

def leftColumns(wargoal, data, side = None):
    result = '|-\n'
    if side is None:
        result += '| %s\n' % pyradox.format.humanString(wargoal, True)
    else:
        result += '| %s (%s)\n' % (pyradox.format.humanString(wargoal, True), side)
    result += '| %s\n' % pyradox.format.humanString(data["type"], True)

    if 'allow_leader_change' in data:
        result += '| {{Icon|yes}}\n'
    else:
        result += '| {{Icon|no}}\n'

    return result

def rightColumns(wargoal, poData):
    result = ''
    result += '| %d%%\n' % (poData['badboy_factor'] * 100)
    result += '| %d%%\n' % (poData['prestige_factor'] * 100)
    result += '| %d%%\n' % (poData['peace_cost_factor'] * 100)

    result += '|'
    for offer, value in poData.items():
        if offer[:3] == 'po_' and value is True:
            result += '\n* %s' % pyradox.format.humanString(offer[3:], True)
    result += '\n'
    return result

w = '{|class = "wikitable sortable"\n'
w += '! Wargoal !! Type !! Warleader<br/>can change !! Aggressive<br/>Expansion !! Prestige !! Cost !! Peace offers\n'
for wargoal, data in tree.items():
    if 'attacker' in data:
        attackerRight = rightColumns(wargoal, data['attacker'])
        defenderRight = rightColumns(wargoal, data['defender'])
        if attackerRight == defenderRight:
            w += leftColumns(wargoal, data)
            w += attackerRight
        else:
            w += leftColumns(wargoal, data, 'attacker')
            w += attackerRight
            w += leftColumns(wargoal, data, 'defender')
            w += defenderRight
    else:
        w += leftColumns(wargoal, data)
        w += rightColumns(wargoal, data)

w += '|}\n'
print(w)
