import _initpath
import os

import pyradox.format

import pyradox

import load.country

idea_map = pyradox.txt.parse_file('out/idea_map.txt')
idea_costs = pyradox.txt.parse_file('out/idea_costs.txt')
non_idea_costs = pyradox.txt.parse_file('out/non_idea_costs.txt')

result = '{|class = "wikitable sortable"\n'
result += '! Country !! Tag !! Territory cost !! Ruler cost !! Government cost !! Technology cost '
result += '!! Idea cost (without ratio) !! Idea cost (with ratio) !! Total cost (without ratio) !! Total cost (with ratio) \n'

for tag, idea_group_name in idea_map.items():
    territory_cost = non_idea_costs[tag]['territory']
    if territory_cost == 0: continue
    early_cost = idea_costs[idea_group_name]['early']
    final_cost = idea_costs[idea_group_name]['final']
    
    ruler_cost = non_idea_costs[tag]['ruler']
    government_cost = non_idea_costs[tag]['government']
    technology_cost = non_idea_costs[tag]['technology']

    total_early_cost = territory_cost + ruler_cost + government_cost + technology_cost + early_cost
    total_final_cost = territory_cost + ruler_cost + government_cost + technology_cost + final_cost
    
    result += '|-\n'

    result += '| %s || %s || %d || %0.1f || %d || %d ' % (
        load.country.get_country_name(tag), tag, territory_cost,
        ruler_cost, government_cost, technology_cost)

    result += '|| %0.1f || %0.1f || %0.1f || %0.1f \n' % (
        early_cost, final_cost, total_early_cost, total_final_cost,
        )

result += '|}\n'

print(result)
