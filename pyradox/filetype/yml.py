import pyradox
import pyradox.token

from pyradox.error import *

import os
import re
import warnings

""" Note that this is .yml as used in Paradox games and not canonical YAML. """

encodings = [
    'utf_8_sig',
    'cp1252',
    ]

# set of sources already read
already_read_sources = set()

# game -> key -> localization
localization_cache = {}

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
    """ Parse the given lines, yielding key-value pairs. """
    for line_number, line in enumerate(lines):
        # Skip comments.
        if re.match(r'\s*#.*', line): continue
        # Skip blank lines.
        if re.match(r'\s*$', line): continue
        
        m = re.match(r'\s*([\w\-\.]+):\d?\s*("*)(.*)(\2)\s*$', line)
        if m is not None:
            key, value = m.group(1, 3)
            yield key.lower(), value
        else:
            # warn
            warnings.warn_explicit('Could not parse line.' % (colorspace_token_string.lower()), ParseWarning, path, line_number)

def parse(s, path=""):
    lines = s.splitlines()
    parse_lines(lines, path)

def parse_file(path):
    """ Return a dictionary containing all key-value pairs in the given file. All keys are lower-case. """
    lines = readlines(path)
    return {key : value for key, value in parse_lines(lines, path)}
    
def parse_dir(path):
    result = {}
    for filename in os.listdir(path):
        fullpath = os.path.join(path, filename)
        if not os.path.isfile(fullpath): continue
        base, ext = os.path.splitext(fullpath)
        if ext != '.yml': continue
        if not re.search('l_%s$' % pyradox.get_language(), base): continue
        result.update(parse_file(fullpath))
    return result
    
def get_localization(key, game):
    if game not in localization_cache:
        localization_path = os.path.join(pyradox.get_game_directory(game), 'localisation')
        localization_cache[game] = parse_dir(localization_path)
    
    if key.lower() in localization_cache[game]:
        return pyradox.token.make_string(localization_cache[game][key.lower()])
    else: 
        return None

def get_localization_desc(key, **kwargs):
    return get_localization('%s_desc' % key, **kwargs)
    
