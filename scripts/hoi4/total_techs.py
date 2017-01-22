import _initpath
import re
import os
import pyradox.hoi4.tech
import pyradox.primitive
import pyradox.struct

techs = pyradox.hoi4.tech.getTechs()["technologies"]

def computeCountryTagAndName(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

def totalTechs(techKeys, filename, date):
    techCount = 0
    techCost = 0.0
    for techKey in techKeys:
        tech = techs[techKey]
        techCount += 1
        techCost += tech['research_cost']

    return techCount, techCost

s = '{|class = "wikitable sortable"\n'
s += '! Country !! Date !! Research slots !! Tech count !! Tech cost !! Since start \n'


for filename, country in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'countries')):
    tag, name = computeCountryTagAndName(filename)
    
    techKeys = set(country['set_technology'].keys())
    date = pyradox.primitive.Date('1936.1.1')
    techSlots = country['set_research_slots'] or 2
    startTechCount, startTechCost = totalTechs(techKeys, filename, date)
    s += '|-\n'
    s += '| %s || %s || %d || %d || %0.1f ||  \n' % (name, date, techSlots, startTechCount, startTechCost)
    for date, effects in country.items():
        if not isinstance(date, pyradox.primitive.Date): continue
        if 'set_technology' not in effects: continue
        techKeys |= set(effects['set_technology'].keys())
        techSlots = country['set_research_slots'] or 2
        techCount, techCost = totalTechs(techKeys, filename, date)
        s += '|-\n'
        s += '| %s || %s || %d || %d || %0.1f || %0.1f \n' % (name, date, techSlots, techCount, techCost, techCost - startTechCost)

s += '|}\n'
print(s)
