from pyradox.datatype.color import Color
from pyradox.datatype.table import Table
from pyradox.datatype.time import Time
from pyradox.datatype.tree import Tree

def to_python(value, **kwargs):
    """
    Converts a value to a built-in Python type.
    """
    if isinstance(value, Tree):
        return value.to_python(**kwargs)
    elif isinstance(value, Time) or isinstance(value, Color):
        return str(value)
    else:
        return value

def match(x, spec):
    if isinstance(spec, str) and isinstance(x, str): return x.lower() == spec.lower()
    else: return x == spec
