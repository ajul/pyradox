import os
import math
import pyradox.config
import pyradox.format
import pyradox.load
import pyradox.txt
import pyradox.struct

parseProvinces, getProvinces = pyradox.load.loadFunctions('EU4', 'provinces', ('history', 'provinces'))

def getProvinceName(provinceID):
    """
    Gets the name a country by its tag according to localization.
    """
    key = 'PROV%d' % provinceID
    return pyradox.yml.getLocalization(key, ['prov_names'])

def provinceCost(province):
    cost = 0
    if 'base_tax' in province:
        cost += province['base_tax'] * 0.5
            
    if 'base_production' in province:
        cost += province['base_production'] * 0.5
        if 'trade_goods' in province and province['trade_goods'] == 'gold':
            cost += province['base_production'] * 3.0
        
    if 'base_manpower' in province:
        cost += province['base_manpower'] * 0.5

    if 'extra_cost' in province:
        cost += province['extra_cost']

    # TODO: terrain mult

    if cost > 0:
        return math.floor(cost)
    else:
        return None
