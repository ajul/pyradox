import _initpath
import os
import re
import math
import collections
import pyradox.config
import pyradox.image
import pyradox

import pyradox.worldmap

import load.country
import load.province

import scipy.stats

countries = load.country.get_countries()

def province_cost(province):
    cost = 0
    if 'base_tax' in province:
        if 'trade_goods' in province and province['trade_goods'] == 'gold':
            cost += 4 * province['base_tax']
        else:
            cost += province['base_tax']
            
    if 'manpower' in province:
        cost += province['manpower']

    if 'extra_cost' in province:
        cost += province['extra_cost']

    if cost > 0:
        return math.floor(cost)
    else:
        return None

def ruler_cost(country, date = pyradox.Date('1444.11.11')):
    monarch = None
    heir = None
    for key, value in country.items():
        if isinstance(key, pyradox.Date):
            if key > date: break
            if 'monarch' in value:
                monarch = value['monarch']
                if heir is not None and monarch['name'] == heir['monarch_name']:
                    monarch_birth = heir_birth
                    heir = None
                else:
                    monarch_birth = key
            if 'heir' in value:
                heir = value['heir']
                heir_birth = key
                next_monarch_name = heir['monarch_name']
    
    cost = 0.0
    if monarch is not None:
        
        skill = sum(monarch[x] for x in ('adm', 'dip', 'mil'))
        age = max(15, (date - monarch_birth) / 365)
        print(skill, age)
        cost += 2 * (skill - 6) * 30 / age
    if heir is not None:
        skill = sum(heir[x] for x in ('adm', 'dip', 'mil'))
        age = (date - heir_birth) / 365
        cost += 2 * (skill - 6) * 30 / (age + 15)
    return cost

governments = pyradox.txt.parse_merge(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'governments'))

def government_cost(country, date = pyradox.Date('1444.11.11')):
    country = country.at_date(date)
    if 'government' not in country: return 0.0
    government = governments[country['government']]
    if 'nation_designer_cost' in government:
        return government['nation_designer_cost']
    else:
        return 0.0

continents = {}
for continent, provinces_id_s in pyradox.txt.parse_file(os.path.join(pyradox.config.basedirs['EU4'], 'map', 'continent.txt')).items():
    for province_id in provinces_id_s:
        if province_id in continents:
            print('Duplicate continent for province %d' % province_id)
        else:
            continents[province_id] = continent

baseline_tech = {
    'europe' : 'western',
    'asia' : 'muslim',
    'africa' : 'muslim',
    'north_america' : 'mesoamerican',
    'south_america' : 'south_american',
    'oceania' : 'south_american',
    }

fallback_continents = {
    'indian' : 'asia',
    'ottoman' : 'europe',
    }

tech_groups = pyradox.txt.parse_file(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'technology.txt'))['groups']

def technology_cost(country, date = pyradox.Date('1444.11.11')):
    country = country.at_date(date)
    if 'valid_for_nation_designer' in tech_groups[country['technology_group']] and not tech_groups[country['technology_group']]['valid_for_nation_designer']:
        return 0.0
    if 'capital' in country:
        continent = continents[country['capital']]
    else:
        continent = fallback_continents[country['technology_group']]
    modifier = tech_groups[country['technology_group']]['modifier']
    baseline = tech_groups[baseline_tech[continent]]['modifier']
    if modifier < baseline:
        return (baseline - modifier) * 100
    else:
        return (baseline - modifier) * 20

government_costs = {}

for tag, country in countries.items():
    if tag in ('NAT', 'PIR', 'REB'): continue
    print(tag)
    government_costs[tag] = [0.0, 0.0, 0.0] # ruler, govt., tech group
    government_costs[tag][0] = ruler_cost(country)
    government_costs[tag][1] = government_cost(country)
    government_costs[tag][2] = technology_cost(country)

provinces = load.province.get_provinces()

territory_costs = {tag : 0.0 for tag in countries.keys()}

for filename, province in provinces.items():
    province = province.at_date(pyradox.Date('1444.11.11'))
    if 'owner' not in province: continue
    territory_costs[province['owner']] += province_cost(province)
    
result = '{|class = "wikitable sortable"\n'
result += '! Country !! Tag !! Territory cost !! Ruler cost !! Government cost !! Technology cost !! Total cost \n'

for tag in sorted(government_costs.keys()):
    if territory_costs[tag] == 0: continue
    result += '|-\n'
    total_cost = sum(government_costs[tag]) + territory_costs[tag]
    result += '| %s || %s || %d || %0.1f || %d || %d || %d \n' % (
        load.country.get_country_name(tag), tag, territory_costs[tag],
        government_costs[tag][0], government_costs[tag][1], government_costs[tag][2],
        total_cost)

result += '|}\n'
print(result)

result_tree = pyradox.Tree()

for tag in sorted(government_costs.keys()):
    nation_tree = pyradox.Tree()
    nation_tree['territory'] = territory_costs[tag]
    nation_tree['ruler'] = government_costs[tag][0]
    nation_tree['government'] = government_costs[tag][1]
    nation_tree['technology'] = government_costs[tag][2]
    result_tree[tag] = nation_tree

outfile = open('out/non_idea_costs.txt', mode = 'w')
outfile.write(str(result_tree))
outfile.close()
