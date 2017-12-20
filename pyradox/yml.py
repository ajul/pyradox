import os
import re
import warnings
import pyradox.config
import pyradox.primitive

from pyradox.error import ParseError, ParseWarning

encodings = [
    'utf_8_sig',
    'cp1252',
    ]

# set of sources already read
already_read_sources = set()
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
        
def parse_lines(lines, filename):
    for line_number, line in enumerate(lines): parse_line(line_number, line, filename)

def parse(s, filename=""):
    lines = s.splitlines()
    parse_lines(lines, filename)

def parse_file(filename):
    lines = readlines(filename)
    parse_lines(lines, filename)
    
def parse_line(line_number, line, filename):
    comment = re.match(r'\s*#.*', line)
    if comment is not None: return
    m = re.match(r'\s*([\w\-\.]+):\d?\s*("*)(.*)(\2)\s*', line)
    if m is not None:
        key, value = m.group(1, 3)
        cache[key.lower()] = value
    else:
        # debug
        warnings.warn(ParseWarning('Could not parse line %s' % line))

def get_localization(key, sources = ['text'], game = None):
    if game is None: game = pyradox.config.default_game
    if isinstance(sources, str):
        sources = [sources]
    for source in sources:
        if source not in already_read_sources:
            language_key = 'l_%s' % pyradox.config.language
            filename = os.path.join(pyradox.config.get_basedir(game), 'localisation', '%s_%s.yml' % (source, language_key))
            
            parse_file(filename)
            already_read_sources.add(source)
            
        if key.lower() in cache:
            return pyradox.primitive.make_string(cache[key.lower()])

    return None

def get_localization_desc(key, **kwargs):
    return get_localization('%s_desc' % key, **kwargs)
    
