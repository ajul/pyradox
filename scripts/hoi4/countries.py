import hoi4
import re
import os
import hoi4


import pyradox



def compute_country_tag_and_name(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

countries = {}
total = pyradox.Tree()

for filename, country in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'countries')):
    tag, name = compute_country_tag_and_name(filename)
    country['tag'] = tag
    ruling_party = country['set_politics']['ruling_party']
    country['name'] = pyradox.yml.get_localization('%s_%s' % (tag, ruling_party), ['countries'], game = 'HoI4')
    countries[tag] = country

states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'states'))
state_categories = pyradox.txt.parse_merge(
    os.path.join(pyradox.get_game_directory('HoI4'), 'common', 'state_category'),
    verbose=False)

for state in states.values():
    history = state['history']
    tag = history['owner']
    country = countries[tag]

    country['states'] = (country['states'] or 0) + 1
    total['states'] = (total['states'] or 0) + 1
    
    state_category_key = state['state_category']
    building_slots = state_categories[state_category_key]['local_building_slots'] or 0
    country['building_slots'] = (country['building_slots'] or 0) + building_slots
    total['building_slots'] = (total['building_slots'] or 0) + building_slots
    
    if 'manpower' in state:
        if (tag in history.find_all('add_core_of')
            or (tag in ['RAJ', 'SIK'])
            or (state['id'] < 200 and state['id'] != 124)):
            manpower_key = 'core_manpower'
        else:
            manpower_key = 'non_core_manpower'
        country[manpower_key] = (country[manpower_key] or 0) + state['manpower']
        total[manpower_key] = (total[manpower_key] or 0) + state['manpower']
    
    if 'resources' in state:
        for resource, quantity in state['resources'].items():
            country[resource] = (country[resource] or 0) + quantity
            total[resource] = (total[resource] or 0) + quantity

    for _, vp_value in history.find_all('victory_points', tuple_length = 2):
        country['victory_points'] = (country['victory_points'] or 0) + vp_value
        total['victory_points'] = (total['victory_points'] or 0) + vp_value

    if 'buildings' in history:
        for building, quantity in history['buildings'].items():
            if isinstance(building, str):
                country[building] = (country[building] or 0) + quantity
                total[building] = (total[building] or 0) + quantity
            else:
                # province buildings
                for building, quantity in quantity.items():
                    country[building] = (country[building] or 0) + quantity
                    total[building] = (total[building] or 0) + quantity

def sum_keys_function(*sum_keys):
    def result_function(k, v):
        return '%d' % sum((v[sum_key] or 0) for sum_key in sum_keys)
    return result_function

columns = (
    ('Country', '{{flag|%(name)s}}'),
    ('Tag', '%(tag)s'),
    ('Ruling party', lambda k, v: v['set_politics']['ruling_party'].title()),
    ('States', '%(states)d'),
    ('Research slots', lambda k, v: '%d' % (v['set_research_slots'] or 2)),
    ('Core population (M)', lambda k, v: ('%0.2f' % (v['core_manpower'] / 1e6)) if 'core_manpower' in v else '' ),
    ('Non-core population (M)', lambda k, v: ('%0.2f' % (v['non_core_manpower'] / 1e6)) if 'non_core_manpower' in v else '' ),
    ('Victory points', '%(victory_points)d'),
    ('Building slots', '%(building_slots)d'),
    ('{{icon|MIC}}', '%(arms_factory)d'),
    ('{{icon|NIC}}', '%(dockyard)d'),
    ('{{icon|CIC}}', '%(industrial_complex)d'),
    ('Total factories', sum_keys_function('arms_factory', 'dockyard', 'industrial_complex')),
    ('{{icon|Oil}}', '%(oil)d'),
    ('{{icon|Aluminium}}', '%(aluminium)d'),
    ('{{icon|Rubber}}', '%(rubber)d'),
    ('{{icon|Tungsten}}', '%(tungsten)d'),
    ('{{icon|Steel}}', '%(steel)d'),
    ('{{icon|Chromium}}', '%(chromium)d'),
    ('Total resources', sum_keys_function('oil', 'aluminium', 'rubber', 'tungsten', 'steel', 'chromium')),
    ('Air base levels', '%(air_base)d'),
    ('Naval base levels', '%(naval_base)d'),
    )

out = open("out/countries.txt", "w")
out.write(pyradox.wiki.make_wikitable(countries, columns, sort_function = lambda key, value: value['name']))
out.close()

print(total)
