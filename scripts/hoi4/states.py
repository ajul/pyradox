import _initpath
import re
import os
import pyradox.hoi4.tech
import pyradox.hoi4.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki
import pyradox.yml

date = '1936.1.1'

localizationSources = ['state_names']

def computeCountryTagAndName(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

countries = {}

for filename, country in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'countries')):
    country = country.atDate(date)
    tag, name = computeCountryTagAndName(filename)
    country['tag'] = tag
    rulingParty = country['set_politics']['ruling_party'] or 'neutrality'
    country['name'] = pyradox.yml.getLocalization('%s_%s' % (tag, rulingParty), ['countries'], game = 'HoI4')
    countries[tag] = country

states = pyradox.txt.parseMerge(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'states'))
stateCategories = pyradox.txt.parseMerge(os.path.join(pyradox.config.getBasedir('HoI4'), 'common', 'state_category'),
                                         verbose=False, mergeLevels = 1)

stateCategories = stateCategories['state_categories']

for state in states.values():
    history = state['history'].atDate(date, mergeLevels = -1)
    # if state['id'] == 50: print('state50', history)
    state['owner'] = history['owner']
    state['owner_name'] = countries[history['owner']]['name']
    state['human_name'] = pyradox.yml.getLocalization(state['name'], localizationSources, game = 'HoI4')
    country = countries[tag]

    country['states'] = (country['states'] or 0) + 1

    stateCategoryKey = state['state_category']
    state['building_slots'] = stateCategories[stateCategoryKey]['local_building_slots'] or 0
    country['building_slots'] = (country['building_slots'] or 0) + state['building_slots']
    
    if 'resources' in state:
        for resource, quantity in state['resources'].items():
            state[resource] = quantity

    for _, victoryPoints in history.findAll('victory_points', tupleLength = 2):
            state['victory_point_total'] = (state['victory_point_total'] or 0) + victoryPoints

    if 'buildings' in history:
        for building, quantity in history['buildings'].items():
            if isinstance(building, str):
                state[building] = (state[building] or 0) + quantity
            else:
                # province buildings
                for building, quantity in quantity.items():
                    state[building] = (state[building] or 0) + quantity

def sumKeysFunction(*sumKeys):
    def resultFunction(k, v):
        return '%d' % sum((v[sumKey] or 0) for sumKey in sumKeys)
    return resultFunction

columns = (
    ('ID', '%(id)s'),
    ('Name', '%(human_name)s'),
    ('Country', '{{flag|%(owner_name)s}}'),
    ('Tag', '%(owner)s'),
    ('Victory points', '%(victory_point_total)d'),
    ('Population (M)', lambda k, v: '%0.2f' % ((v['manpower'] or 0) / 1e6) ),
    ('Infrastructure', '%(infrastructure)d'),
    ('Building slots', '%(building_slots)d'),
    ('Military factories', '%(arms_factory)d'),
    ('Naval dockyards', '%(dockyard)d'),
    ('Civilian factories', '%(industrial_complex)d'),
    # ('Total factories', sumKeysFunction('arms_factory', 'dockyard', 'industrial_complex')),
    ('{{Icon|Oil}}', '%(oil)d'),
    ('{{Icon|Aluminium}}', '%(aluminium)d'),
    ('{{Icon|Rubber}}', '%(rubber)d'),
    ('{{Icon|Tungsten}}', '%(tungsten)d'),
    ('{{Icon|Steel}}', '%(steel)d'),
    ('{{Icon|Chromium}}', '%(chromium)d'),
    # ('Total resources', sumKeysFunction('oil', 'aluminium', 'rubber', 'tungsten', 'steel', 'chromium')),
    ('Air base levels', '%(air_base)d'),
    ('Naval base levels', '%(naval_base)d'),
    )

out = open("out/states.txt", "w")
out.write(pyradox.wiki.makeWikitable(states, columns, sortFunction = lambda item: item[1]['id']))
out.close()
