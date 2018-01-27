import _initpath
import os

import pyradox
import load.country
import load.province



def output_row(data):
    result = "|-\n"
    result += "| %(name)s || %(country)s || %(date)s || %(adm)s || %(dip)s || %(mil)s || %(total)s || %(fire)s || %(shock)s || %(manuever)s || %(siege)s \n" % data
    return result

# Load countries and provinces.
countries = load.country.get_countries()

leader_keys = ('fire', 'shock', 'manuever', 'siege')

s = '{|class = "wikitable sortable"\n'
s += "! Leader !! Country !! Date !! {{icon|adm}} !! {{icon|dip}} !! {{icon|mil}} !! Total !! {{icon|leader fire}} !! {{icon|leader shock}} !! {{icon|leader maneuver}} !! {{icon|leader siege}} \n"

for tag, country in countries.items():
    country_name = load.country.get_country_name(tag)
    if country_name is None: print('Missing localization: ' + tag)

    for date, data in country.items():
        if not isinstance(date, pyradox.Date): continue
        for ruler in data.find_all('monarch'):
            if "leader" in ruler:
                for key in leader_keys:
                    ruler[key] = str(ruler['leader'][key])
            else:
                for key in leader_keys:
                    ruler[key] = ''
            if 'regent' in ruler and ruler['regent']: ruler['name'] += ' (regent)'
            # broken file
            if not isinstance(ruler['mil'], int): ruler['mil'] = 0
            ruler['total'] = ruler['adm'] + ruler['dip'] + ruler['mil']
            ruler["country"] = country_name
            ruler["date"] = date
            s += output_row(ruler)


s += '|}\n'
print(s)
