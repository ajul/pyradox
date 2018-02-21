import os

import pyradox


parse_countries, get_countries = pyradox.load.load_functions('EU4', 'countries', ('history', 'countries'))

def get_country_name(tag):
    """
    Gets the name a country by its tag according to localization.
    """
    return pyradox.yml.get_localization(tag, game = 'EU4')
