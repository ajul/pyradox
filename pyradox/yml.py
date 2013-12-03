import os
import yaml
import pyradox.config
import pyradox.primitive

cache = {}

def getLocalization(key, sources = ['text'], game = pyradox.config.defaultGame):
    if isinstance(sources, str):
        sources = [sources]
    for source in sources:
        if source not in cache:
            languageKey = 'l_%s' % pyradox.config.language
            filename = os.path.join(pyradox.config.basedirs[game], 'localisation', '%s_%s.yml' % (source, languageKey))
            
            f = open(filename, encoding='utf-8-sig')
            data = yaml.load(f)
            f.close()
            cache[source] = data[languageKey]

        if key in cache[source]:
            return pyradox.primitive.makeString(cache[source][key])
        elif key.upper() in cache[source]:
            return pyradox.primitive.makeString(cache[source][key.upper()])
    
    return None

def getLocalizationDesc(key, sources = ['text']):
    return getLocalization('%s_desc' % key, sources)
    
