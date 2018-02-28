import _initpath
import pyradox
import os
import copy
import math

slot_sizes = ['S', 'M', 'L']
ship_types = ['corvette', 'destroyer', 'cruiser', 'battleship', 'titan', 'platform']

armor_techs = [
    'Nanocomposite Materials',
    'Ceramo-Metal Materials',
    'Plasteel Materials',
    'Durasteel Materials',
    'Neutronium Materials',
    'Artificial Dragonscales',
    ]

armor_components = [
    'Nanocomposite Armor',
    'Ceramo-Metal Armor',
    'Plasteel Armor',
    'Durasteel Armor',
    'Neutronium Armor',
    'Dragonscale Armor',
    ]

armor_columns = ['cost', 'armor']

shield_components = ['Deflectors', 'Improved Deflectors', 'Shields', 'Advanced Shields', 'Hyper Shields',
               'Psionic Shields', 'Enigmatic Deflectors']
shield_techs = [x + ' tech' for x in shield_components]
shield_columns = ['cost', 'power', 'shield']

reactors = ['Fission', 'Fusion', 'Cold Fusion', 'Antimatter', 'Zero-Point', 'Dark Matter']
reactor_techs = [x + ' Power' for x in reactors]
reactor_techs[-1] = 'Enigmatic Power Generation'
reactor_columns = ['cost', 'power']
reactor_components = [x + ' Reactor' for x in reactors]

armor_data = pyradox.parse_file(['common',
                                  'component_templates',
                                  '00_utilities.txt'],
                                 game = 'Stellaris')

shield_data = pyradox.parse_file(['common',
                                  'component_templates',
                                  '00_utilities_shields.txt'],
                                 game = 'Stellaris')

reactor_data = pyradox.parse_file(['common',
                                  'component_templates',
                                  '00_utilities_reactors.txt'],
                                 game = 'Stellaris')

def make_table_body(techs, components, columns, data, slot_sizes):
    result = ''
    for tier0, (tech, component) in enumerate(zip(techs, components)):
        result += '|-\n| '

        row = ['{{icon|%s|32px}} %s' % (tech, component)]
        
        for slot_size in slot_sizes:
            for column in columns:
                key_a = '@%s_%s%d' % (column, slot_size, tier0 + 1)
                key_b = '@%s_%d%s' % (column, tier0 + 1, slot_size)
                key_c = '@%s_%s_%d' % (slot_size, column, tier0 + 1)
                value = data[key_a]
                if value is None: value = data[key_b]
                if value is None: value = data[key_c]
                value = abs(value)
                row.append(str(value))
        result += ' || '.join(row)
        result += '\n'

    result += '|}\n'
    return result

print(make_table_body(armor_techs, armor_components, armor_columns, armor_data, slot_sizes))
print(make_table_body(shield_techs, shield_components, shield_columns, shield_data, slot_sizes))
print(make_table_body(reactor_techs, reactor_components, reactor_columns, reactor_data, ship_types))
