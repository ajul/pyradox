import os
import pyradox.config
import pyradox.format
import pyradox.txt
import pyradox.struct

# Lazy loading.
provinces = None

def parseProvinces():
    result = pyradox.struct.Tree()
    for filename, tree in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces')):
        provinceID, name = pyradox.format.splitFilename(filename)
        result.append(provinceID, tree)

    print('Loaded provinces.')
    return result

def getProvinces():
    """
    Get a copy of the country Tree, parsing if necessary.
    Maps tag -> country data.
    """
    global provinces
    if provinces is None: provinces = parseProvinces()
    return provinces.deepCopy()

def getProvinceName(provinceID):
    """
    Gets the name a country by its tag according to localization.
    """
    key = 'PROV%d' % provinceID
    return pyradox.yml.getLocalization(key, ['prov_names'])
