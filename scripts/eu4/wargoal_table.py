import _initpath
import os
import re
import collections



import pyradox

tree = pyradox.parse_file(os.path.join(pyradox.get_game_directory('EU4'), 'common', 'wargoal_types', '00_wargoal_types.txt'))

def left_columns(wargoal, data, side = None):
    result = '|-\n'
    if side is None:
        result += '| %s\n' % pyradox.format.human_string(wargoal, True)
    else:
        result += '| %s (%s)\n' % (pyradox.format.human_string(wargoal, True), side)
    result += '| %s\n' % pyradox.format.human_string(data["type"], True)

    if 'allow_leader_change' in data:
        result += '| {{Icon|yes}}\n'
    else:
        result += '| {{Icon|no}}\n'

    return result

def right_columns(wargoal, po_data):
    result = ''
    result += '| %d%%\n' % (po_data['badboy_factor'] * 100)
    result += '| %d%%\n' % (po_data['prestige_factor'] * 100)
    result += '| %d%%\n' % (po_data['peace_cost_factor'] * 100)

    result += '|'
    for offer, value in po_data.items():
        if offer[:3] == 'po_' and value is True:
            result += '\n* %s' % pyradox.format.human_string(offer[3:], True)
    result += '\n'
    return result

w = '{|class = "wikitable sortable"\n'
w += '! Wargoal !! Type !! Warleader<br/>can change !! Aggressive<br/>Expansion !! Prestige !! Cost !! Peace offers\n'
for wargoal, data in tree.items():
    if 'attacker' in data:
        attacker_right = right_columns(wargoal, data['attacker'])
        defender_right = right_columns(wargoal, data['defender'])
        if attacker_right == defender_right:
            w += left_columns(wargoal, data)
            w += attacker_right
        else:
            w += left_columns(wargoal, data, 'attacker')
            w += attacker_right
            w += left_columns(wargoal, data, 'defender')
            w += defender_right
    else:
        w += left_columns(wargoal, data)
        w += right_columns(wargoal, data)

w += '|}\n'
print(w)
