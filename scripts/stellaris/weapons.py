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

csv_data = pyradox.csv.parse_file(['common',
                                   'component_templates',
                                   'weapon_components.csv'],
                                  game = 'Stellaris')

txt_data = pyradox.parse_merge(['common', 'component_templates'], game = 'Stellaris')

total_data = pyradox.Tree()

for weapon in txt_data.find_all('weapon_component_template'):
    if weapon['hidden']: continue
    key = weapon['key']
    total_data[key] = weapon + csv_data[key]

def compute_average_damage(key, value):
    return '%0.1f' % (value['min_damage'] + value['max_damage'])

def compute_normalized_dps(key, value):
    dps_per_size = (0.5 * (value['min_damage'] + value['max_damage']) / value['cooldown'] / slot_sizes[value['size']])
    effectiveness_mult = 0.5 * value['hull_damage'] + 0.25 * value['armor_damage'] + 0.25 * value['shield_damage']
    accuracy_mult = value['accuracy']
    return '%0.2f' % (dps_per_size * effectiveness_mult)

def float_to_255(x):
    x = round(255.0 * x)
    return max(min(x, 255), 0)

def to_html_color(c):
    return '#%02x%02x%02x' % c

def compute_color(key, value):

    hull = 0.5
    armor = 0.5 * (value['armor_damage'] / value['hull_damage'] + value['armor_penetration'])
    shield = 0.5 * (value['shield_damage'] / value['hull_damage'] + value['shield_penetration'])

    c = (float_to_255(armor), float_to_255(hull), float_to_255(shield))
    return to_html_color(c)

def compute_special_description(key, value):
    hull = value['hull_damage']
    armor = value['armor_damage']
    shield = value['shield_damage']

    ap = value['armor_penetration']
    sp = value['shield_penetration']

    if ap >= 0.5 and sp >= 0.5:
        text = 'penetrating'
    elif ap >= 0.5:
        text = 'armor-penetrating'
    elif sp >= 0.5:
        text = 'shield-penetrating'
    elif hull > armor and hull > shield:
        text = 'anti-hull'
    elif armor > hull and armor > shield:
        text = 'anti-armor'
    elif shield > hull and shield > armor:
        text = 'anti-shield'
    else:
        text = 'general-purpose'

    color = compute_color(key, value)

    return '<span style="color:%s; font-weight: bold;">%s</span>' % (color, text)

def compute_special(key, value):
    items = [compute_special_description(key, value)]

    if value['hull_damage'] != 1.0:
        items.append('%d%% hull damage' % (value['hull_damage'] * 100.0))

    if value['armor_damage'] != 1.0:
        items.append('%d%% armor damage' % (value['armor_damage'] * 100.0))

    if value['armor_penetration'] != 0.0:
        items.append('%d%% armor penetration' % (value['armor_penetration'] * 100.0))
    
    if value['shield_damage'] != 1.0:
        items.append('%d%% shield damage' % (value['shield_damage'] * 100.0))

    if value['shield_penetration'] != 0.0:
        items.append('%d%% shield penetration' % (value['shield_penetration'] * 100.0))
    
    return '<br/>'.join(items)

def is_missile(key, value):
    return value['missile_speed'] > 0.0

column_specs = [
    ('Key', '%(key)s'),
    ('Size', '%(size)s'),
    ('Minerals', '%(cost)s'),
    ('Power', '%(power)s'),
    ('Damage', compute_average_damage),
    ('Cooldown', '%(cooldown)d'),
    ('Normalized DPS', compute_normalized_dps),
    ('Range', '%(range)s'),
    ('Accuracy', '%(accuracy)s'),
    ('Tracking', '%(tracking)s'),
    ('Special', compute_special),
    ]

missile_specs = [
    ('Key', '%(key)s'),
    ('Speed', '%(missile_speed)d'),
    ('Evasion', '%(missile_evasion)0.2f'),
    ('Hull', '%(missile_health)d'),
    #('Armor', '%(missile_armor).1f'),
    #('Shield', '%(missile_shield).1f'),
    ]

with open('out/weapons.wiki', 'w') as outfile:
    outfile.write(pyradox.filetype.table.make_table(total_data, 'wiki', column_specs))   

with open('out/missiles.wiki', 'w') as outfile:
    outfile.write(pyradox.filetype.table.make_table(total_data, 'wiki', missile_specs, filter_function = is_missile))   
