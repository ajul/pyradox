from pyradox.datatype import *
from pyradox.error import *

import re

"""
Token handling. The end-user should not ever have to deal with this directly.
"""
    
def make_bool(token_string):
    """
    Converts a token string to a boolean.
    """
    if token_string in ('yes', 'true'): return True
    elif token_string in ('no', 'false'): return False
    else: raise ValueError('Invalid token string %s for bool.' % token_string)

def make_string(token_string):
    """
    Converts a token string to a string by dequoting it.
    """
    return re.sub(r'^"(.*)"$', r'\1', token_string)

def make_token_string(value):
    """
    Converts a primitive value to a token string.
    """
    if isinstance(value, bool):
        if value: return 'yes'
        else: return 'no'
    elif isinstance(value, float):
        # Only go to 3 decimal places.
        return ('%0.3f' % value).rstrip('0')
    elif isinstance(value, str):
        #quote string if contains non-alphanumerics or is empty
        if len(value) == 0 or re.search("\W", value):
            return '"%s"' % value
        else:
            return value
    else:
        return str(value)
    
token_patterns = [
    ('time', r'\d+\.\d+\.\d+(\.\d+)?\b'),
    ('float', r'-?(\d+\.\d*|\d*\.\d+)\b'),
    ('int', r'-?\d+\b'),
    ('bool', r'(yes|no)\b'),
    ('str', r'"([^"\\\n]|\\.)*["\n]|[^#=\{\}\s]+'), # allow strings to end with newline instead of "; do escape characters exist?
]

key_constructors = {
    'time' : Time,
    'int' : int,
    'str' : str,
    }

constructors = {
    'time' : Time,
    'float' : float,
    'int' : int,
    'bool' : make_bool,
    'str' : make_string,
    }
    
def primitive_type_of(token_string):
    for token_type, pattern in token_patterns:
        m = re.match(pattern + '$', token_string)
        if m: return token_type
    return None
    
def is_primitive_key_token_type(token_type):
    return token_type in key_constructors.keys()
    
def is_primitive_value_token_type(token_type):
    return token_type in constructors.keys()

def make_primitive(token_string, token_type = None, default_token_type = None):
    if token_type is None:
        token_type = primitive_type_of(token_string)
        if token_type is None:
            if default_token_type is None:
                raise ParseError('Unrecognized token "%s". Should not occur.' % (token_string,))
            else:
                token_type = default_token_type
    return constructors[token_type](token_string)
