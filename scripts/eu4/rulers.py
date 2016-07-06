import _initpath
import os
import pyradox.config
import pyradox.txt
import pyradox.eu4.country
import pyradox.eu4.province
import pyradox.primitive
import pyradox.yml

def outputRow(data):
    result = "|-\n"
    result += "| %(name)s || %(country)s || %(date)s || %(adm)s || %(dip)s || %(mil)s || %(total)s || %(fire)s || %(shock)s || %(manuever)s || %(siege)s \n" % data
    return result

# Load countries and provinces.
countries = pyradox.eu4.country.getCountries()

leaderKeys = ('fire', 'shock', 'manuever', 'siege')

s = '{|class = "wikitable sortable"\n'
s += "! Leader !! Country !! Date !! {{icon|adm}} !! {{icon|dip}} !! {{icon|mil}} !! Total !! {{icon|leader fire}} !! {{icon|leader shock}} !! {{icon|leader maneuver}} !! {{icon|leader siege}} \n"

for tag, country in countries.items():
    countryName = pyradox.eu4.country.getCountryName(tag)
    if countryName is None: print('Missing localization: ' + tag)

    for date, data in country.items():
        if not isinstance(date, pyradox.primitive.Date): continue
        for ruler in data.findAll('monarch'):
            if "leader" in ruler:
                for key in leaderKeys:
                    ruler[key] = str(ruler['leader'][key])
            else:
                for key in leaderKeys:
                    ruler[key] = ''
            if 'regent' in ruler and ruler['regent']: ruler['name'] += ' (regent)'
            # broken file
            if not isinstance(ruler['mil'], int): ruler['mil'] = 0
            ruler['total'] = ruler['adm'] + ruler['dip'] + ruler['mil']
            ruler["country"] = countryName
            ruler["date"] = date
            s += outputRow(ruler)


s += '|}\n'
print(s)
