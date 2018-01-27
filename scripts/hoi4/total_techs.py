import _initpath
import re
import os
import hoi4

import pyradox

techs = hoi4.load.get_technologies()

def compute_country_tag_and_name(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

def total_techs(tech_keys, filename, date):
    tech_count = 0
    tech_cost = 0.0
    for tech_key in tech_keys:
        tech = techs[tech_key]
        tech_count += 1
        tech_cost += tech['research_cost']

    return tech_count, tech_cost

s = '{|class = "wikitable sortable"\n'
s += '! Country !! Date !! Research slots !! Tech count !! Tech cost !! Since start \n'


for filename, country in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'countries')):
    tag, name = compute_country_tag_and_name(filename)
    
    tech_keys = set(country['set_technology'].keys())
    date = pyradox.Date('1936.1.1')
    tech_slots = country['set_research_slots'] or 2
    start_tech_count, start_tech_cost = total_techs(tech_keys, filename, date)
    s += '|-\n'
    s += '| %s || %s || %d || %d || %0.1f ||  \n' % (name, date, tech_slots, start_tech_count, start_tech_cost)
    for date, effects in country.items():
        if not isinstance(date, pyradox.Date): continue
        if 'set_technology' not in effects: continue
        tech_keys |= set(effects['set_technology'].keys())
        tech_slots = country['set_research_slots'] or 2
        tech_count, tech_cost = total_techs(tech_keys, filename, date)
        s += '|-\n'
        s += '| %s || %s || %d || %d || %0.1f || %0.1f \n' % (name, date, tech_slots, tech_count, tech_cost, tech_cost - start_tech_cost)

s += '|}\n'
print(s)
