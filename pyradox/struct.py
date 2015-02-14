import pyradox.primitive
import re
import os
import inspect
import copy

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
    
    class _Item():
        """
        Internal class to keep track of items.
        preComments appear before the item, one per line.
        lineComments appear on the same line as the item.
        """
        def __init__(self, key, value, preComments = None, lineComment = None):
            self.key = key
            self.value = value
            if preComments is None: self.preComments = []
            else: self.preComments = preComments
            self.lineComment = lineComment
        
        def prettyprint(self, level = 0, indentString = '    '):
            result = ''
            for preComment in self.preComments:
                result += indentString * level + "#" + preComment + '\n'
            result += indentString * level + pyradox.primitive.makeTokenString(self.key) + ' = '
            if isinstance(self.value, Tree) or isinstance(self.value, List):
                result += '{\n'
                result += self.value.prettyprint(level + 1)
                result += indentString * level + '}'
            else:
                result += pyradox.primitive.makeTokenString(self.value)
            
            if self.lineComment is not None:
                result += indentString * level + " #" + self.lineComment
            result += '\n'
            return result
    
    def __init__(self, iterator = None, endComments = None):
        """Creates an tree from a key, value iterator if given, or an empty tree otherwise."""
        if iterator is None:
            self._data = []
        else:
            self._data = [Tree._Item(key, value) for (key, value) in iterator]
            
        if endComments is None: self.endComments = []
        else: self.endComments = endComments
        
    # iterator methods
    def keys(self):
        """Iterator over the keys of this tree."""
        for item in self._data: yield item.key

    def values(self):
        """Iterator over the values of this tree."""
        for item in self._data: yield item.value

    def items(self):
        """Iterator over (key, value) pairs of this tree."""
        for item in self._data: yield item.key, item.value
        
    def comments(self):
        """Iterator over (key, value) pairs of this tree."""
        for item in self._data: yield item.preComments, item.lineComment

    def __contains__(self, key):
        """True iff key is in the top level of the tree."""
        return self.contains(key)
        
    def contains(self, *args, **kwargs):
        """True iff key is in the tree. recurse = True for recursive."""
        return self.find(*args, **kwargs) is not None

    def __iter__(self):
        """Iterator over the keys of this tree."""
        for key in self.keys(): yield key
        
    def __len__(self):
        """Number of key-value pairs."""
        return len(self._data)

    # read/find methods
    def at(self, i):
        """Return (key, value) by index"""
        item = self._data[i]
        return item.key, item.value

    def keyAt(self, i):
        """Return the ith key."""
        return self._data[i].key

    def valueAt(self, i):
        """Return the ith value."""
        return self._data[i].value
        
    def setLineCommentAt(self, i, lineComment):
        self._data[i].lineComment = lineComment
        
    def setPreCommentsAt(self, i, preComments):
        self._data[i].preComments = preComments

    def indexOf(self, key):
        for i, item in enumerate(self._data):
            if match(key, item.key): return i
        return None
        
    def find(self, *args, **kwargs):
        """Return the first or last value corresponding to a key or None if not found"""
        it = self.findAll(*args, **kwargs)
        return next(it, None)

    def findAll(self, key, reverse = False, recurse = False):
        """Return all values corresponding to a key or None if not found"""
        it = self._data
        if reverse: it = reversed(it)
        for item in it:
            if match(key, item.key): yield item.value
            if recurse and isinstance(item.value, Tree):
                for result in item.value.findWalk(key, reverse = reverse, recurse = recurse): yield result

    def __getitem__(self, query):
        """Return the LAST value corresponding to a key or None if not found"""
        return self.find(query, reverse = True)

    # write methods
    def append(self, key, value, preComments = None, lineComment = None):
        """Append a new key, value pair"""
        self._data.append(Tree._Item(key, value, preComments, lineComment))

    def insert(self, i, key, value):
        """Insert a new key, value pair at a numeric position"""
        self._data.insert(i, Tree._Item(key, value))

    def __setitem__(self, key, value):
        """Replaces the first item with the key if it exists; otherwise appends it"""
        for i, item in enumerate(self._data):
            if match(key, item.key):
                self._data[i] = Tree._Item(key, value)
                return
        else:
            self.append(key, value)

    def __delitem__(self, key):
        """Delete an item from the tree"""
        # TODO: delete all?
        idx = self.indexOf(key)
        if idx is not None: del self._data[idx]

    # TODO: add, iadd
    # TODO: update
    
    # string output methods
    def __repr__(self):
        """Produces a string in the original .txt format."""
        return self.prettyprint(0)
    
    def prettyprint(self, level = 0, indentString = '    '):
        result = ''
        for item in self._data:
            result += item.prettyprint(level, indentString)
                
        for endComment in self.endComments:
            result += indentString * level + '#' + endComment + '\n'
        return result

    # other methods
    def atDate(self, date = False):
        """
        returns a deep copy of this tree with all date blocks at or before the specified date deep copied and promoted to the top and the rest omitted
        if date is True, use all date blocks
        if date is False, use no date blocks
        """
        # cast to date
        if date not in (True, False):
            date = pyradox.primitive.Date(date)
        
        result = Tree()
        # non-dates
        for item in self._data:
            if not isinstance(item.key, pyradox.primitive.Date):
                result.append(item.key, copy.deepcopy(item.value))

        # dates
        if date is False: return result
        
        for item in self._data:
            if isinstance(item.key, pyradox.primitive.Date):
                if date is True or item.key <= date:
                    for item in item.value._data:
                        result[item.key] = copy.deepcopy(item.value)
        return result

class List(Struct):
    """
    List class. Like a standard list, but with a different string representation.
    """
    
    class _Item():
        """
        Internal class to keep track of items.
        preComments appear before the item, one per line.
        lineComments appear on the same line as the item.
        """
        def __init__(self, value, preComments = None, lineComment = None):
            self.value = value
            if preComments is None: self.preComments = []
            else: self.preComments = preComments
            self.lineComment = lineComment
        
        def prettyprint(self, level = 0, indentString = '    '):
            result = ''
            for preComment in self.preComments:
                result += indentString * level + "#" + preComment + '\n'
                
            result += indentString * level
            
            if isinstance(self.value, Tree) or isinstance(self.value, List):
                result += '{\n'
                result += self.value.prettyprint(level + 1)
                result += indentString * level + '}'
            else:
                result += pyradox.primitive.makeTokenString(self.value)
                
            if self.lineComment is not None:
                result += " #" + self.lineComment
            result += '\n'
            return result
    
    def __init__(self, iterator = None, endComments = None):
        if iterator is None: self._data = []
        else: self._data = [List._Item(value) for value in iterator]
        
        if endComments is None: self.endComments = []
        else: self.endComments = endComments
    
    def __repr__(self):
        """Produces a string in the original .txt format."""
        return self.prettyprint(0)
        
    def __contains__(self, value):
        for item in self._data:
            if item.value == value: return True
        return False
        
    def __iter__(self):
        for item in self._data: yield item.value
        
    def __getitem__(self, query):
        """Return the LAST value corresponding to a key or None if not found"""
        return self.find(query, reverse = True)

    # write methods
    def append(self, value, preComments = None, lineComment = None):
        """Append a new value"""
        self._data.append(List._Item(value, preComments, lineComment))

    def insert(self, i, value):
        """Insert a new value"""
        self._data.insert(i, List._Item(value))

    def __setitem__(self, key, value):
        """Replaces a value"""
        self._data[i] = List._Item(value)
        
    def setLineComment(self, i, lineComment):
        self._data[i].lineComment = lineComment
        
    def setPreComments(self, i, preComments):
        self._data[i].preComments = preComments
    
    # TODO: add, iadd

    def prettyprint(self, level = 0, indentString = '    '):
        result = ''
        for item in self._data:
            result += item.prettyprint(level, indentString)
        for endComment in self.endComments:
            result += indentString * level + '#' + endComment + '\n'
        return result
            
def match(x, spec):
    if isinstance(spec, str) and isinstance(x, str): return x.lower() == spec.lower()
    else: return x == spec
