import pyradox.primitive
import re
import os
import inspect

class Struct():
    """
    for isinstance only
    """
    pass

class Tree(Struct):
    """
    Tree class representing Paradox .txt files.
    Supports most features of OrderedDict and some of ElementTree.
    Keys are stored with case but are matched non-case-sensitive.
    """
    def __init__(self, iterator = None):
        """Creates an tree from a key, value iterator if given, or an empty tree otherwise."""
        if iterator is None:
            self._data = []
        else:
            self._data = [(key, value) for (key, value) in iterator]
        
    # iterator methods
    def keys(self):
        """Iterator over the keys of this tree."""
        for x in self._data: yield x[0]

    def values(self):
        """Iterator over the values of this tree."""
        for x in self._data: yield x[1]

    def items(self):
        """Iterator over (key, value) pairs of this tree."""
        for x in self._data: yield x

    def __contains__(self, query):
        """True iff at least one key matches they query"""
        return self.find(query) is not None

    def __iter__(self):
        """Iterator over the keys of this tree."""
        yield from self.keys()
        
    def __len__(self):
        """Number of key-value pairs."""
        return len(self._data)

    # read/find methods
    def at(self, query):
        """Return (key, value) by index"""
        return self._data[query]

    def keyAt(self, query):
        """Return the queryth key."""
        return self._data[query][0]

    def valueAt(self, query):
        """Return the queryth value."""
        return self._data[query][1]

    def indexOf(self, query):
        """Return the first index of a key or None if not found"""
        for i, (key, value) in enumerate(self._data):
            if match(key, query): return i
        return None

    def find(self, query):
        """Return the first value corresponding to a key or None if not found"""
        for key, value in self._data:
            if match(key, query): return value
        return None

    def __getitem__(self, query):
        """Return the first value corresponding to a key or None if not found"""
        return self.find(query)

    def findAll(self, query):
        """Iterator over all values whose key matches the query""" 
        for key, value in self._data:
            if match(key, query): yield value

    def findWalk(self, query):
        """Iterator over all values whose key matches the query; looks recursively"""
        for key, value in self._data:
            if match(key, query):
                yield value
            if isinstance(value, Tree):
                yield from value.findWalk(query)

    def containsValueWalk(self, query):
        """Returns true iff the query appears as a value anywhere in the tree."""
        for key, value in self._data:
            if match(value, query):
                return True
            if isinstance(value, Tree) and value.containsValueWalk(query):
                return True
        return False

    def copy(self):
        """returns a shallow copy"""
        return Tree(x for x in self._data)

    def deepCopy(self):
        """returns a deep copy"""    
        return Tree((key, deepCopy(value)) for (key, value) in self._data)

    # write methods
    def append(self, key, value):
        """Append a new key, value pair"""
        self._data.append((key, value))

    def insert(self, i, key, value):
        self._data.insert(i, (key, value))

    def __setitem__(self, key, value):
        """Replaces the first item with the key if it exists; otherwise appends it"""
        for i, (oldKey, oldValue) in enumerate(self._data):
            if match(oldKey, key):
                self._data[i] = (key, value)
                return
        else:
            self.append(key, value)

    def __delitem__(self, key):
        """Delete an item from the tree"""
        idx = self.indexOf(key)
        if idx is not None: del self._data[idx]

    def __add__(self, other):
        """Shallow concatenation of two trees"""
        result = Tree()
        result._data = self._data + other._data
        return result
        
    def __iadd__(self, other):
        """Concatenate a Tree to this one"""
        self._data += other._data
        return self

    def update(self, other):
        """Update this Tree with another Tree or dict"""
        for key, value in other.items():
            self[key] = value

    def deleteWalk(self, query):
        """Delete all items with the key recursively"""
        toRemove = []
        for key, value in self._data:
            if match(key, query):
                toRemove.append((key, value))

        for item in toRemove:
            self._data.remove(item)

        for key, value in self._data:
            if isinstance(value, Tree):
                value.deleteWalk(query)

        # TODO: option to prune empty subtrees?

    # string output methods
    def __repr__(self):
        """Produces a string in the original .txt format."""
        return self.prettyprint(0)
    
    def prettyprint(self, level = 0, indentString = '    '):
        result = ''
        for key, value in self._data:
            result += indentString * level + pyradox.primitive.makeTokenString(key) + ' = '
            if isinstance(value, Tree) or isinstance(value, List):
                result += '{\n'
                result += value.prettyprint(level + 1)
                result += indentString * level + '}\n'
            else:
                result += pyradox.primitive.makeTokenString(value)
                result += '\n'
        return result

    # other methods
    def atDate(self, date = False):
        """
        returns a copy of this tree with all date blocks at or before the specified date deepcopied and promoted to the top and the rest omitted
        if date is True, use all date blocks
        if date is False, use no date blocks
        """
        # cast to date
        if date not in (True, False):
            date = pyradox.primitive.Date(date)
        
        result = Tree()
        # non-dates
        for key, value in self._data:
            if not isinstance(key, pyradox.primitive.Date):
                result.append(key, deepCopy(value))

        # dates
        if date is False: return result
        
        for key, value in self._data:
            if isinstance(key, pyradox.primitive.Date):
                if date is True or key <= date:
                    for subkey, subvalue in value.items():
                        result[subkey] = deepCopy(subvalue)
        return result

class List(list, Struct):
    """
    List class. Like a standard list, but with a different string representation.
    """
    
    def __repr__(self):
        """Produces a string in the original .txt format."""
        return self.prettyprint(0)

    def prettyprint(self, level = 0, indentString = '    '):
        result = ''
        for value in self:
            if isinstance(value, Struct):
                result += '{\n'
                result += value.prettyprint(level + 1)
                result += indentString * level + '}\n'
            else:
                result += pyradox.primitive.makeTokenString(value)
                result += ' '
        return result

    def copy(self):
        """returns a shallow copy"""
        return List(x for x in self)

    def deepCopy(self):
        """returns a deep copy"""    
        return List(deepCopy(x) for x in self)
            

def match(x, spec):
    if isinstance(spec, str) and isinstance(x, str): return x.lower() == spec.lower()
    else: return x == spec

def deepCopy(value):
    if isinstance(value, Struct):
        return value.deepCopy()
    else:
        return value

