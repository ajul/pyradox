import _initpath
import os
import pyradox.config
import pyradox.txt
import pyradox.eu4.country
import pyradox.eu4.province
import pyradox.primitive
import pyradox.yml

# Load countries and provinces.
countries = pyradox.eu4.country.getCountries()
provinces = pyradox.eu4.province.getProvinces()

# Initialize total provincial values.
for country in countries.values():
    country['provinces'] = 0
    country['base_tax'] = 0.0
    country['manpower'] = 0.0

# Global stats.
totalBaseTax = 0.0
totalManpower = 0.0

# Total up provincial values.
for province in provinces.values():
    # Update province to start date.
    province = province.atDate('1444.11.11')
    # Don't count unowned provinces.
    if 'owner' not in province: continue
    # Tally things up.
    tag = province['owner']
    country = countries[tag]
    country['provinces'] += 1
    if 'base_tax' in province:
        country['base_tax'] += province['base_tax']
        totalBaseTax += province['base_tax']
    if 'manpower' in province:
        country['manpower'] += province['manpower']
        totalManpower += province['manpower']

w = '{|class = "wikitable sortable"\n'
w += '! Country !! Tech group !! Religion !! Primary culture !! Provinces !! Base tax !! Base kManpower\n'

for tag, country in countries.items():
    country = country.atDate('1444.11.11')
    country['name'] = pyradox.eu4.country.getCountryName(tag)
    country['technology_group'] = pyradox.yml.getLocalization(country['technology_group'] or '')
    country['religion'] = pyradox.yml.getLocalization(country['religion'] or '')
    country['primary_culture'] = pyradox.yml.getLocalization(country['primary_culture'] or '')
    w += '|-\n'
    w += '| %(name)s || %(technology_group)s || %(religion)s || %(primary_culture)s ' % country
    w += '|| %(provinces)d || %(base_tax)d || %(manpower)d \n' % country
w += '|}\n'

print(w)
print(totalBaseTax, totalManpower)
