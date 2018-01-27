import pyradox.datatype.color
import pyradox.datatype.time
import pyradox.datatype.tree

def to_python(value, **kwargs):
    """
    Converts a value to a built-in Python type.
    """
    if isinstance(value, pyradox.datatype.tree.Tree):
        return value.to_python(**kwargs)
    elif isinstance(value, pyradox.datatype.time.Time) or isinstance(value, pyradox.datatype.color.Color):
        return str(value)
    else:
        return value

def match(x, spec):
    if isinstance(spec, str) and isinstance(x, str): return x.lower() == spec.lower()
    else: return x == spec