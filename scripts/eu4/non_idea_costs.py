import _initpath
import os
import re
import math
import collections
import pyradox.config
import pyradox.image
import pyradox.txt
import pyradox.primitive
import pyradox.worldmap

import pyradox.eu4.country
import pyradox.eu4.province

import scipy.stats

countries = pyradox.eu4.country.getCountries()

def provinceCost(province):
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

def rulerCost(country, date = pyradox.primitive.Date('1444.11.11')):
    monarch = None
    heir = None
    for key, value in country.items():
        if isinstance(key, pyradox.primitive.Date):
            if key > date: break
            if 'monarch' in value:
                monarch = value['monarch']
                if heir is not None and monarch['name'] == heir['monarch_name']:
                    monarchBirth = heirBirth
                    heir = None
                else:
                    monarchBirth = key
            if 'heir' in value:
                heir = value['heir']
                heirBirth = key
                nextMonarchName = heir['monarch_name']
    
    cost = 0.0
    if monarch is not None:
        
        skill = sum(monarch[x] for x in ('adm', 'dip', 'mil'))
        age = max(15, (date - monarchBirth) / 365)
        print(skill, age)
        cost += 2 * (skill - 6) * 30 / age
    if heir is not None:
        skill = sum(heir[x] for x in ('adm', 'dip', 'mil'))
        age = (date - heirBirth) / 365
        cost += 2 * (skill - 6) * 30 / (age + 15)
    return cost

governments = pyradox.txt.parseMerge(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'governments'))

def governmentCost(country, date = pyradox.primitive.Date('1444.11.11')):
    country = country.atDate(date)
    if 'government' not in country: return 0.0
    government = governments[country['government']]
    if 'nation_designer_cost' in government:
        return government['nation_designer_cost']
    else:
        return 0.0

continents = {}
for continent, provincesIDs in pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'map', 'continent.txt')).items():
    for provinceID in provincesIDs:
        if provinceID in continents:
            print('Duplicate continent for province %d' % provinceID)
        else:
            continents[provinceID] = continent

baselineTech = {
    'europe' : 'western',
    'asia' : 'muslim',
    'africa' : 'muslim',
    'north_america' : 'mesoamerican',
    'south_america' : 'south_american',
    'oceania' : 'south_american',
    }

fallbackContinents = {
    'indian' : 'asia',
    'ottoman' : 'europe',
    }

techGroups = pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'technology.txt'))['groups']

def technologyCost(country, date = pyradox.primitive.Date('1444.11.11')):
    country = country.atDate(date)
    if 'valid_for_nation_designer' in techGroups[country['technology_group']] and not techGroups[country['technology_group']]['valid_for_nation_designer']:
        return 0.0
    if 'capital' in country:
        continent = continents[country['capital']]
    else:
        continent = fallbackContinents[country['technology_group']]
    modifier = techGroups[country['technology_group']]['modifier']
    baseline = techGroups[baselineTech[continent]]['modifier']
    if modifier < baseline:
        return (baseline - modifier) * 100
    else:
        return (baseline - modifier) * 20

governmentCosts = {}

for tag, country in countries.items():
    if tag in ('NAT', 'PIR', 'REB'): continue
    print(tag)
    governmentCosts[tag] = [0.0, 0.0, 0.0] # ruler, govt., tech group
    governmentCosts[tag][0] = rulerCost(country)
    governmentCosts[tag][1] = governmentCost(country)
    governmentCosts[tag][2] = technologyCost(country)

provinces = pyradox.eu4.province.getProvinces()

territoryCosts = {tag : 0.0 for tag in countries.keys()}

for filename, province in provinces.items():
    province = province.atDate(pyradox.primitive.Date('1444.11.11'))
    if 'owner' not in province: continue
    territoryCosts[province['owner']] += provinceCost(province)
    
result = '{|class = "wikitable sortable"\n'
result += '! Country !! Tag !! Territory cost !! Ruler cost !! Government cost !! Technology cost !! Total cost \n'

for tag in sorted(governmentCosts.keys()):
    if territoryCosts[tag] == 0: continue
    result += '|-\n'
    totalCost = sum(governmentCosts[tag]) + territoryCosts[tag]
    result += '| %s || %s || %d || %0.1f || %d || %d || %d \n' % (
        pyradox.eu4.country.getCountryName(tag), tag, territoryCosts[tag],
        governmentCosts[tag][0], governmentCosts[tag][1], governmentCosts[tag][2],
        totalCost)

result += '|}\n'
print(result)

resultTree = pyradox.struct.Tree()

for tag in sorted(governmentCosts.keys()):
    nationTree = pyradox.struct.Tree()
    nationTree['territory'] = territoryCosts[tag]
    nationTree['ruler'] = governmentCosts[tag][0]
    nationTree['government'] = governmentCosts[tag][1]
    nationTree['technology'] = governmentCosts[tag][2]
    resultTree[tag] = nationTree

outfile = open('out/non_idea_costs.txt', mode = 'w')
outfile.write(str(resultTree))
outfile.close()
