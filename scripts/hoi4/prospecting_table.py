import hoi4
import hoi4.state
import os
import math
import re
import collections

import pyradox

from PIL import Image

game = 'HoI4'

def generate_row(decision_id, decision):
    row = pyradox.Tree()

    row['id'] = decision_id
    if 'has_tech' in decision['available']:
        tech = decision['available']['has_tech']
        row['tech_type'] = tech[:-1]
        row['tech_level'] = tech[-1]
    else:
        row['tech_type'] = ''
        row['tech_level'] = ''
        
    row['cic'] = decision['modifier']['civilian_factory_use']
    
    if isinstance(decision['days_remove'], int):
        row['time'] = decision['days_remove']
    else:
        # TODO: determine from code?
        row['time'] = 30

    if 'fire_only_once' in decision:
        pass
    else:
        row['repeatable'] = decision['visible'].find('value', recurse = True, default = 1)

    for effect_key, effect in decision['remove_effect'].items():
        if not isinstance(effect_key, int): continue
        if 'add_resource' in effect:
            row['state'] = effect_key
            row['resource'] = effect['add_resource']['type']
            row['amount'] = effect['add_resource']['amount']

    row['state_name'] = hoi4.state.get_state_name(row['state'])
    row['owner_name'] = hoi4.state.get_state_owner(row['state'])['name']
    row['cost'] = row['cic'] * row['time'] * 5
    
    return row

# Load resource decisions.
decisions = pyradox.txt.parse_file(['common', 'decisions', 'resource_prospecting.txt'], game = game)

table = pyradox.Tree()

for decision_id, decision in decisions['prospect_for_resources'].items():
    row = generate_row(decision_id, decision)
    table.append(decision_id, row)

columns = (
    ('State', '%(state_name)s'),
    ('Owner (1936)', '{{flag|%(owner_name)s}}'),
    ('Tech type', '%(tech_type)s'),
    ('Tech level', '%(tech_level)s'),
    ('{{icon|cic}}', '%(cic)s'),
    ('{{icon|time}}', '%(time)s'),
    ('{{icon|construction cost}}', '%(cost)d'),
    ('Resource', '{{icon|%(resource)s}} %(resource)s'),
    ('Amount', '%(amount)d'),
    ('Repeatable', '%(repeatable)d'),
    )

print(pyradox.table.make_table(table, 'wiki', columns,
                               sort_function = lambda key, value: (value['owner_name'], value['tech_level'], value['state_name'])))
