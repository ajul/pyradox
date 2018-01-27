import _initpath
import re
import os
import pyradox.config
import pyradox.primitive
import pyradox.struct
import pyradox.wiki
import pyradox.yml

def compute_country_tag_and_name(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

economics = pyradox.txt.parse_file(
    os.path.join(pyradox.config.get_basedir('HoI4'),
                 'common', 'ideas', '_economic.txt'))['ideas']

result = pyradox.struct.Tree()

for filename, country in pyradox.txt.parse_dir(os.path.join(pyradox.config.get_basedir('HoI4'), 'history', 'countries')):
    country = country.at_time('1936.1.1')
    tag, name = compute_country_tag_and_name(filename)
    country['tag'] = tag
    ruling_party = country['set_politics']['ruling_party']
    country['name'] = pyradox.yml.get_localization('%s_%s' % (tag, ruling_party), ['countries'], game = 'HoI4')
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
out.write(pyradox.wiki.make_wikitable(result, columns,
                                     sort_function = lambda item: item[1]['name'],
                                     table_style = None))
out.close()
