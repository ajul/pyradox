import os
import pyradox.format
import pyradox.config
import pyradox.struct
import pyradox.txt
import pyradox.yml

# Lazy loading.
cache = {}

def parseCountries(basedir = None):
    if basedir is None: basedir = pyradox.config.basedirs['EU4']
    result = pyradox.struct.Tree()
    for filename, tree in pyradox.txt.parseDir(os.path.join(basedir, 'history', 'countries')):
        tag, rawName = pyradox.format.splitFilename(filename)
        result.append(tag, tree)
    print('Loaded countries.')
    return result

def getCountries(basedir = None):
    """
    Get a copy of the country Tree, parsing if necessary.
    Maps tag -> country data.
    """
    if basedir is None: basedir = pyradox.config.basedirs['EU4']
    if basedir not in cache: cache[basedir] = parseCountries(basedir)
    return cache[basedir].deepCopy()

def getCountryName(tag):
    """
    Gets the name a country by its tag according to localization.
    """
    return pyradox.yml.getLocalization(tag, ['text', 'countries'])
