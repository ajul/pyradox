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

# game -> key -> localisation
localisation_cache = {}

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
    
def parse_walk(path):
    result = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            fullpath = os.path.join(root, file)
            base, ext = os.path.splitext(file)
            if ext != '.yml': continue
            if not re.search('l_%s$' % pyradox.get_language(), base): continue
            result.update(parse_file(fullpath))
    return result
    
def get_localisation(key, game, process_substitutions = True):
    """
    process_substitutions: If true, items between $ signs will be replaced with the localisation with that key.
    """
    def replace_substitution(m):
        return get_localisation(m.group(1), game, process_substitutions = True) or ''
    
    if game not in localisation_cache:
        localisation_path = os.path.join(pyradox.get_game_directory(game), 'localisation')
        localisation_cache[game] = parse_walk(localisation_path)
    
    if key.lower() in localisation_cache[game]:
        result = pyradox.token.make_string(localisation_cache[game][key.lower()])
        if process_substitutions:
            # TODO: are $ signs escapable?
            result = re.sub(r'\$(.*?)\$', replace_substitution, result)
        return result
    else: 
        return None

def get_localisation_desc(key, **kwargs):
    return get_localisation('%s_desc' % key, **kwargs)

def to_yml(dictionary):
    result = 'l_english:\n'
    for key, value in dictionary.items():
        value = re.sub('"', '\\"', value)
        result += ' %s:0 "%s"\n' % (key, value)
    return result
