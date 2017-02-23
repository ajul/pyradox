import os
import re
import warnings
import pyradox.config
import pyradox.primitive

encodings = [
    'utf_8_sig',
    'cp1252',
    ]

# set of sources already read
alreadyReadSources = set()
# key -> value
cache = {}

def readlines(filename):
    for encoding in encodings:
        try:
            f = open(filename, encoding=encoding)
            lines = f.readlines()
            f.close()
            return lines
        except UnicodeDecodeError:
            warnings.warn(ParseWarning("Failed to decode input file %s using codec %s." % (filename, encoding)))
            f.close()
    raise ParseError("All codecs failed for input file %s." % filename)

class ParseError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class ParseWarning(Warning):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
        
def parseLines(lines, filename):
    for lineNumber, line in enumerate(lines): parseLine(lineNumber, line, filename)

def parse(s, filename=""):
    lines = s.splitlines()
    parseLines(lines, filename)

def parseFile(filename):
    lines = readlines(filename)
    parseLines(lines, filename)
    
def parseLine(lineNumber, line, filename):
    comment = re.match(r'\s*#.*', line)
    if comment is not None: return
    m = re.match(r'\s*([\w-]+):\d?\s*("*)(.*)(\2)\s*', line)
    if m is not None:
        key, value = m.group(1, 3)
        cache[key.lower()] = value
    else:
        # debug
        warnings.warn(ParseWarning('Could not parse line %s' % line))

def getLocalization(key, sources = ['text'], game = None):
    if game is None: game = pyradox.config.defaultGame
    if isinstance(sources, str):
        sources = [sources]
    for source in sources:
        if source not in alreadyReadSources:
            languageKey = 'l_%s' % pyradox.config.language
            filename = os.path.join(pyradox.config.getBasedir(game), 'localisation', '%s_%s.yml' % (source, languageKey))
            
            parseFile(filename)
            alreadyReadSources.add(source)
            
        if key.lower() in cache:
            return pyradox.primitive.makeString(cache[key.lower()])

    return None

def getLocalizationDesc(key, **kwargs):
    return getLocalization('%s_desc' % key, **kwargs)
    
