import os
import pyradox.format
import pyradox.config
import pyradox.load
import pyradox.struct
import pyradox.txt
import pyradox.yml

parseCountries, getCountries = pyradox.load.loadFunctions('EU4', 'countries', ('history', 'countries'))

def getCountryName(tag):
    """
    Gets the name a country by its tag according to localization.
    """
    return pyradox.yml.getLocalization(tag, ['EU4', 'text', 'countries', 'nw2', 'res_publica', 'aow', 'eldorado', 'tags_phase4'])
