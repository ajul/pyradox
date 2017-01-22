import _initpath
import re
import os
import pyradox.hoi4.tech
import pyradox.hoi4.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki
import pyradox.yml

def computeCountryTagAndName(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

def listCommanderTraits(k, v):
    if 'traits' not in v: return ''
    result = ''
    for trait in v.findAll('traits'):
        if not isinstance(trait, str): continue
        result += '{{iconify|' + pyradox.yml.getLocalization(trait, ['traits'], game = 'HoI4') + '}}, '
    return result[:-2]

commanderTypeKeys = {
    'create_field_marshal' : 'Field Marshal',
    'create_corps_commander' : 'General',
    'create_navy_leader' : 'Admiral',
    }

columns = (
    ('Country', '{{flag|%(country)s}}', None),
    ('Name', '%(name)s', None),
    ('Type', lambda k, v: commanderTypeKeys[k], None),
    ('Skill', '%(skill)d', None),
    ('Traits', listCommanderTraits, None),
    )

commanders = pyradox.struct.Tree()

for filename, country in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'countries')):
    tag, _ = computeCountryTagAndName(filename)
    rulingParty = country['set_politics']['ruling_party']
    countryName = pyradox.yml.getLocalization('%s_%s' % (tag, rulingParty), ['countries'], game = 'HoI4')
    for commanderTypeKey in commanderTypeKeys.keys():
        for leader in country.findAll(commanderTypeKey):
            leader['country'] = countryName
            commanders.append(commanderTypeKey, leader)

out = open("out/military_commanders.txt", "w", encoding="utf-8")
out.write(pyradox.wiki.makeWikitable(commanders, columns, sortFunction = lambda item: (item[1]['country'], item[0], item[1]['name'])))
out.close()
