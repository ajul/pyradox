import os
import pyradox.config
import pyradox.format
import pyradox.load
import pyradox.txt
import pyradox.struct

parseProvinces, getProvinces = pyradox.load.loadFunctions('EU4', 'provinces', ('history', 'provinces'), False)

def getProvinceName(provinceID):
    """
    Gets the name a country by its tag according to localization.
    """
    key = 'PROV%d' % provinceID
    return pyradox.yml.getLocalization(key, ['prov_names'])
