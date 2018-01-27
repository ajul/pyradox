import _initpath
import re
import os
import json
import load.tech
import load.unit
import pyradox

date = '1936.1.1'

beta = False

if beta:
    game = 'HoI4_beta'
else:
    game = 'HoI4'

localization_sources = ['state_names']

def compute_country_tag_and_name(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

countries = {}

for filename, country in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory(game), 'history', 'countries')):
    country = country.at_time(date)
    tag, name = compute_country_tag_and_name(filename)
    country['tag'] = tag
    ruling_party = country['set_politics']['ruling_party'] or 'neutrality'
    country['name'] = pyradox.yml.get_localization('%s_%s' % (tag, ruling_party), ['countries'], game = 'HoI4')
    countries[tag] = country

states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory(game), 'history', 'states'))
state_categories = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory(game), 'common', 'state_category'),
                                         verbose=False, merge_levels = 1)

state_categories = state_categories['state_categories']

for state in states.values():
    history = state['history'].at_time(date, merge_levels = -1)
    # if state['id'] == 50: print('state50', history)
    state['owner'] = history['owner']
    state['owner_name'] = countries[history['owner']]['name']
    state['human_name'] = pyradox.yml.get_localization(state['name'], localization_sources, game = game)
    country = countries[tag]

    country['states'] = (country['states'] or 0) + 1

    state_category_key = state['state_category']
    state['building_slots'] = state_categories[state_category_key]['local_building_slots'] or 0
    country['building_slots'] = (country['building_slots'] or 0) + state['building_slots']
    
    if 'resources' in state:
        for resource, quantity in state['resources'].items():
            state[resource] = quantity

    for _, victory_points in history.find_all('victory_points', tuple_length = 2):
            state['victory_point_total'] = (state['victory_point_total'] or 0) + victory_points

    if 'buildings' in history:
        for building, quantity in history['buildings'].items():
            if isinstance(building, str):
                state[building] = (state[building] or 0) + quantity
            else:
                # province buildings
                for building, quantity in quantity.items():
                    state[building] = (state[building] or 0) + quantity

def sum_keys_function(*sum_keys):
    def result_function(k, v):
        return '%d' % sum((v[sum_key] or 0) for sum_key in sum_keys)
    return result_function

columns = (
    ('ID', '%(id)s'),
    ('Name', '%(human_name)s'),
    ('Country', '{{flag|%(owner_name)s}}'),
    ('Tag', '%(owner)s'),
    ('{{Icon|vp}}', '%(victory_point_total)d'),
    ('{{Icon|pop|(M)}}', lambda k, v: '%0.2f' % ((v['manpower'] or 0) / 1e6) ),
    ('{{Icon|infra}}', '%(infrastructure)d'),
    ('State category', '%(state_category)s'),
    ('Building slots', '%(building_slots)d'),
    ('{{Icon|MIC}}', '%(arms_factory)d'),
    ('{{Icon|NIC}}', '%(dockyard)d'),
    ('{{Icon|CIC}}', '%(industrial_complex)d'),
    # ('Total factories', sum_keys_function('arms_factory', 'dockyard', 'industrial_complex')),
    ('{{Icon|Oil}}', '%(oil)d'),
    ('{{Icon|Aluminium}}', '%(aluminium)d'),
    ('{{Icon|Rubber}}', '%(rubber)d'),
    ('{{Icon|Tungsten}}', '%(tungsten)d'),
    ('{{Icon|Steel}}', '%(steel)d'),
    ('{{Icon|Chromium}}', '%(chromium)d'),
    # ('Total resources', sum_keys_function('oil', 'aluminium', 'rubber', 'tungsten', 'steel', 'chromium')),
    ('{{Icon|Air base}}', '%(air_base)d'),
    ('{{Icon|Naval base}}', '%(naval_base)d'),
    )

if beta:
    out_filename = "out/states_beta.txt"
else:
    out_filename = "out/states.txt"
out = open(out_filename, "w")
out.write(pyradox.wiki.make_wikitable(states, columns, sort_function = lambda key, value: value['id']))
out.close()

if beta:
    csv_filename = "out/states_beta.csv"
else:
    csv_filename = "out/states.csv"

pyradox.csv.write_csv(csv_filename, states, columns, 'excel', sort_function = lambda key, value: value['id'])

if beta:
    json_filename = "out/states_beta.json"
else:
    json_filename = "out/states.json"

with open(json_filename, 'w') as f:
    pyradox.json.dump_tree(states.replace_key_with_subkey('state', 'id'), f)
