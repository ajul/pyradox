import _initpath
import os

import pyradox
import load.country
import load.province



def leader_row(leader):
    result = "|-\n"
    result += "| %(name)s || %(country)s || %(start_date)s || %(death_date)s || %(type)s || %(fire)d || %(shock)d || %(manuever)d || %(siege)d \n" % leader
    return result

# Load countries and provinces.
countries = load.country.get_countries()

leaders = ()

s = '{|class = "wikitable sortable"\n'
s += "! Leader !! Country !! Start date !! End date !! Type !! Fire !! Shock !! Manuever !! Siege \n"

# Initialize total provincial values.
for tag, country in countries.items():
    country_name = load.country.get_country_name(tag)

    for date, data in country.items():
        if not isinstance(date, pyradox.Date): continue
        for leader in data.find_all('leader'):
            leader["country"] = country_name
            leader["start_date"] = date
            s += leader_row(leader)
        for monarch in data.find_all('monarch'):
            if "leader" not in monarch: continue
            leader = monarch["leader"]
            leader["country"] = country_name
            leader["start_date"] = date
            leader["death_date"] = "(monarch)"
            s += leader_row(leader)

s += '|}'

print(s)
