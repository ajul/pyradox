import _initpath
import pyradox
import os
import copy
import math

slot_sizes = {
    'small' : 1,
    'point_defence' : 1,
    'medium' : 2,
    'torpedo' : 2,
    'large' : 4,
    'extra_large' : 8,
    'titanic' : 16, #?
    'planet_killer' : 1,
    }

slot_icons = {
    'small' : 's',
    'point_defence' : 'pd',
    'medium' : 'm',
    'torpedo' : 'g',
    'large' : 'l',
    'extra_large' : 'xl',
    'titanic' : 't',
    'planet_killer' : 'wd',
    }

csv_data = pyradox.csv.parse_file(['common',
                                   'component_templates',
                                   'weapon_components.csv'],
                                  game = 'Stellaris')

txt_data = pyradox.parse_merge(['common',
                                'component_templates'], game = 'Stellaris')

total_data = pyradox.Tree()

for weapon in txt_data.find_all('weapon_component_template'):
    if weapon['hidden']: continue
    key = weapon['key']
    total_data[key] = weapon + csv_data[key]

column_specs = [
    ('Weapon', lambda k, v: pyradox.get_localisation(k, game = 'Stellaris')),
    ('Size', compute_slot),
    ('Minerals', '%(cost)d'),
    ('Power', lambda k, v: str(abs(v['power']))),
    ('Average<br/>damage', compute_average_damage),
    ('Cooldown', '%(cooldown)d'),
    ('Normalized DPS', compute_normalized_dps),
    ('Range', '%(range)d'),
    ('Accuracy', lambda k, v: '%d%%' % (v['accuracy'] * 100.0)),
    ('Tracking', lambda k, v: '%d%%' % (v['tracking'] * 100.0)),
    ('Modifiers', compute_special),
    ]

missile_specs = [
    ('Missile', lambda k, v: pyradox.get_localisation(k, game = 'Stellaris')),
    ('Speed', '%(missile_speed)d'),
    ('Evasion', lambda k, v: '%d%%' % (v['missile_evasion'] * 100.0)),
    ('Hull', '%(missile_health)d'),
    #('Armor', '%(missile_armor).1f'),
    #('Shield', '%(missile_shield).1f'),
    ]

with open('out/weapons.wiki', 'w') as outfile:
    outfile.write(pyradox.filetype.table.make_table(total_data, 'wiki', column_specs))   

with open('out/missiles.wiki', 'w') as outfile:
    outfile.write(pyradox.filetype.table.make_table(total_data, 'wiki', missile_specs, filter_function = is_missile))   
