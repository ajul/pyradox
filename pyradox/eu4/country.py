import os
import pyradox.format
import pyradox.config
import pyradox.load
import pyradox.struct
import pyradox.txt
import pyradox.yml

parseCountries, getCountries = pyradox.load.loadFunctions('EU4', 'countries', ('history', 'countries'), False)

def getCountryName(tag):
    """
    Gets the name a country by its tag according to localization.
    """
    return pyradox.yml.getLocalization(tag, ['text', 'countries'])
