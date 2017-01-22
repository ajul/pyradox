import _initpath
import re
import os
import pyradox.config
import pyradox.primitive
import pyradox.struct
import pyradox.wiki
import pyradox.yml

def computeCountryTagAndName(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

economics = pyradox.txt.parseFile(
    os.path.join(pyradox.config.getBasedir('HoI4'),
                 'common', 'ideas', '_economic.txt'))['ideas']

result = pyradox.struct.Tree()

for filename, country in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'countries')):
    country = country.atDate('1936.1.1')
    tag, name = computeCountryTagAndName(filename)
    country['tag'] = tag
    rulingParty = country['set_politics']['ruling_party']
    country['name'] = pyradox.yml.getLocalization('%s_%s' % (tag, rulingParty), ['countries'], game = 'HoI4')
    result[tag] = country

    if 'add_ideas' in country:
        for idea in country['add_ideas']:
            if idea in economics['economy']:
                country['economy'] = idea
            elif idea in economics['trade_laws']:
                country['trade_laws'] = idea
    country['economy'] = country['economy'] or 'civilian_economy'
    country['trade_laws'] = country['trade_laws'] or 'export_focus'

columns = [
    ('Country', '%(name)s', None),
    ('Tag', '%(tag)s', None),
    ('Economy', '%(economy)s', None),
    ('Trade', '%(trade_laws)s', None),
    ]

out = open("out/initial_laws.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.wiki.makeWikitable(result, columns,
                                     sortFunction = lambda item: item[1]['name'],
                                     tableStyle = None))
out.close()
