import _initpath
import pyradox
import os
import copy
import math
import stellaris.weapon

txt_data = pyradox.parse_merge(['common',
                                'component_templates'], game = 'Stellaris', apply_defines = True)

default_values = pyradox.Tree()
default_values['hull_damage'] = 1.0
default_values['armor_damage'] = 1.0
default_values['shield_damage'] = 1.0
default_values['armor_penetration'] = 0.0
default_values['shield_penetration'] = 0.0
default_values['tracking'] = 0.0
default_values['prerequisites'] = 'Ship part strike craft scout 1'

result_data = pyradox.Tree()

for strike_craft in txt_data.find_all('strike_craft_component_template'):
    if strike_craft['hidden']: continue
    key = strike_craft['key']
    strike_craft.weak_update(default_values)
    strike_craft['size'] = 'hangar'
    result_data[key] = strike_craft

column_specs = [
    ('Weapon', stellaris.weapon.icon_and_name),
    ('Size', stellaris.weapon.slot_string),
    ('{{icon|minerals}}<br/>Cost', '%(cost)d'),
    ('{{icon|power}}<br/>Power', lambda k, v: str(abs(v['power']))),
    ('{{icon|damage}}<br/>Average<br/>damage', lambda k, v: '%0.1f' % stellaris.weapon.average_damage(v)),
    ('{{icon|time}}<br/>Cooldown', '%(cooldown)d'),
    ('{{icon|damage}}/{{icon|time}}<br/>Normalized DPS', lambda k, v: '%0.1f' % stellaris.weapon.normalized_dps(v)),
    ('{{icon|weapons range}}<br/>Range', '%(range)d'),
    ('{{icon|ship accuracy}}<br/>Accuracy', lambda k, v: '%d%%' % (v['accuracy'] * 100.0)),
    ('{{icon|tracking}}<br/>Tracking', lambda k, v: '%d%%' % (v['tracking'] * 100.0)),
    ('Modifiers', stellaris.weapon.special_string),
    ('{{icon|ship health}}<br/>Hull', '%(health)d'),
    ('{{icon|shield}}<br/>Shield', '%(shield)d'),
    ('{{icon|evasion}}<br/>Evasion', lambda k, v: '%d%%' % (v['evasion'] * 100.0)),
    ('{{icon|ship speed}}<br/>Speed', '%(speed)d'),
    ]

with open('out/strike_craft.wiki', 'w') as outfile:
    outfile.write(pyradox.filetype.table.make_table(
        result_data, 'wiki',
        column_specs,
        table_classes = ["wikitable sortable mw-collapsible mw-collapsed"]))   

