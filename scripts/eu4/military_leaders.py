import _initpath
import os
import pyradox.config
import pyradox.txt
import pyradox.eu4.country
import pyradox.eu4.province
import pyradox.primitive
import pyradox.yml

def leaderRow(leader):
    result = "|-\n"
    result += "| %(name)s || %(country)s || %(start_date)s || %(death_date)s || %(type)s || %(fire)d || %(shock)d || %(manuever)d || %(siege)d \n" % leader
    return result

# Load countries and provinces.
countries = pyradox.eu4.country.getCountries()

leaders = ()

s = '{|class = "wikitable sortable"\n'
s += "! Leader !! Country !! Start date !! End date !! Type !! Fire !! Shock !! Manuever !! Siege \n"

# Initialize total provincial values.
for tag, country in countries.items():
    countryName = pyradox.eu4.country.getCountryName(tag)

    for date, data in country.items():
        if not isinstance(date, pyradox.primitive.Date): continue
        for leader in data.findAll('leader'):
            leader["country"] = countryName
            leader["start_date"] = date
            s += leaderRow(leader)
        for monarch in data.findAll('monarch'):
            if "leader" not in monarch: continue
            leader = monarch["leader"]
            leader["country"] = countryName
            leader["start_date"] = date
            leader["death_date"] = "(monarch)"
            s += leaderRow(leader)

s += '|}'

print(s)
