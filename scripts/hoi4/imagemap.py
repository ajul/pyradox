import hoi4
import csv
import os
import re
import collections


import pyradox


from PIL import Image

# province IDs to ignore
ignore = [13204]

date = pyradox.Time('1936.1.1')
#date = pyradox.Time('1939.8.14')

def compute_country_tag_and_name(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'states'))


# tag -> name

country_names = {}

for filename, country in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'countries')):
    tag, name = compute_country_tag_and_name(filename)
    ruling_party = country['set_politics']['ruling_party'] or 'neutrality'
    country_names[tag] = pyradox.yml.get_localisation('%s_%s' % (tag, ruling_party), game = 'HoI4')

# tag -> provinces

country_provinces = {}

for state in states.values():
    history = state['history'].at_time(date)
    controller = history['controller'] or history['owner']

    if controller not in country_provinces: country_provinces[controller] = []
    
    for province_id in state.find_all('provinces'):
        if not province_id in ignore:
            country_provinces[controller].append(province_id)

links = []
for tag, province_ids in country_provinces.items():
    link = '[[%s]]' % country_names[tag]
    links.append((province_ids, link))

province_map = pyradox.worldmap.ProvinceMap(game = 'HoI4')


print(province_map.generate_imagemap('File:Political map.png|thumb|800px|center|Countries in 1936.', links))
