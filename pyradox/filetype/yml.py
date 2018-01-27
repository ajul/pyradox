import pyradox
import pyradox.token

from pyradox.error import *

import os
import re
import warnings

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
            with open(filename, encoding=encoding) as f:
                lines = f.readlines()
            return lines
        except UnicodeDecodeError:
            warnings.warn(ParseWarning("Failed to decode input file %s using codec %s." % (filename, encoding)))
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
    m = re.match(r'\s*([\w\-\.]+):\d?\s*("*)(.*)(\2)\s*$', line)
    if m is not None:
        key, value = m.group(1, 3)
        cache[key.lower()] = value
    else:
        # warn if not blank
        if not re.match(r'\s*$', line):
            warnings.warn(ParseWarning('Could not parse line %s' % line))

def get_localization(key, sources = ['text'], game = None):
    if isinstance(sources, str):
        sources = [sources]
    for source in sources:
        if source not in already_read_sources:
            language_key = 'l_%s' % pyradox.get_language()
            filename = os.path.join(pyradox.get_game_directory(game), 'localisation', '%s_%s.yml' % (source, language_key))
            
            parse_file(filename)
            already_read_sources.add(source)
            
        if key.lower() in cache:
            return pyradox.token.make_string(cache[key.lower()])

    return None

def get_localization_desc(key, **kwargs):
    return get_localization('%s_desc' % key, **kwargs)
    
