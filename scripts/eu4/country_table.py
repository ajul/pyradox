import _initpath
import os

import pyradox
import load.country
import load.province

import pyradox.yml

# Load countries and provinces.
countries = load.country.get_countries()
provinces = load.province.get_provinces()

# Initialize total provincial values.
for country in countries.values():
    country['provinces'] = 0
    country['base_tax'] = 0.0
    country['manpower'] = 0.0

# Global stats.
total_base_tax = 0.0
total_manpower = 0.0

# Total up provincial values.
for province in provinces.values():
    # Update province to start date.
    province = province.at_date('1444.11.11')
    # Don't count unowned provinces.
    if 'owner' not in province: continue
    # Tally things up.
    tag = province['owner']
    country = countries[tag]
    country['provinces'] += 1
    if 'base_tax' in province:
        country['base_tax'] += province['base_tax']
        total_base_tax += province['base_tax']
    if 'manpower' in province:
        country['manpower'] += province['manpower']
        total_manpower += province['manpower']

w = '{|class = "wikitable sortable"\n'
w += '! Country !! Tech group !! Religion !! Primary culture !! Provinces !! Base tax !! Base k_manpower\n'

for tag, country in countries.items():
    country = country.at_date('1444.11.11')
    country['name'] = load.country.get_country_name(tag)
    country['technology_group'] = pyradox.yml.get_localization(country['technology_group'] or '')
    country['religion'] = pyradox.yml.get_localization(country['religion'] or '')
    country['primary_culture'] = pyradox.yml.get_localization(country['primary_culture'] or '')
    w += '|-\n'
    w += '| %(name)s || %(technology_group)s || %(religion)s || %(primary_culture)s ' % country
    w += '|| %(provinces)d || %(base_tax)d || %(manpower)d \n' % country
w += '|}\n'

print(w)
print(total_base_tax, total_manpower)
