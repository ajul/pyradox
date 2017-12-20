import pyradox.primitive
import re
import os
import inspect
import copy
import json

class Tree():
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
        postComments appear after the item, one per line.
        """
        def __init__(self, key, value, operator = None, inGroup = False, preComments = None, lineComment = None, postComments = None):
            self.key = key
            self.value = value
            
            if preComments is None: self.preComments = []
            else: self.preComments = preComments
            
            self.lineComment = lineComment
            
            if postComments is None: self.postComments = []
            else: self.postComments = postComments
            
            if operator is None: self.operator = '='
            else: self.operator = operator
            
            self.inGroup = inGroup

        #For JSON output
        def rawData(self):
            if isinstance(self.value, Tree) or isinstance(self.value, List):
                return self.value.rawData()
            else:
                return self.value

        def prettyprint(self, level, indentString, includeComments):
            result = ''
            if includeComments:
                for preComment in self.preComments:
                    result += '%s#%s\n' % (indentString * level, preComment)
            
            # Output key.
            result += '%s%s %s ' % (indentString * level, self.key, self.operator)
            
            # Output value.
            if isinstance(self.value, Tree):
                result += '{\n'
                result += self.value.prettyprint(level + 1)
                result += indentString * level + '}'
            else:
                result += pyradox.primitive.makeTokenString(self.value)
            
            if includeComments and self.lineComment is not None:
                result += " #%s" % (self.lineComment)
                
            result += '\n'
            
            if includeComments:
                for postComment in self.postComments:
                    result += '%s#%s\n' % (indentString * level, preComment)
            
            return result
            
        def prettyprintGroup(self, level, indentString, includeComments):
            """
            Some trickiness here. Assumes that any indentation for the first line has already been performed.
            If there are no comments, return (value string, False), so following values may be placed on the same line.
            Otherwise, return (string ending in newline, True).
            """
            result = ''
            needIndent = False
            hasPreComment = False
            if includeComments:
                for preComment in self.preComments:
                    hasPreComment = True
                    result += '\n%s#%s' % (indentString * level, preComment)
            
            if hasPreComment:
                result += '\n%s' % (indentString * level)
            
            # Output value. At current trees are not valid inside groups.
            result += pyradox.primitive.makeTokenString(self.value) + ' '
            
            if includeComments and self.lineComment is not None:
                needIndent = True
                result += "#%s" % (self.lineComment)
            
            if includeComments:
                for postComment in self.postComments:
                    needIndent = True
                    result += '\n%s#%s' % (indentString * level, postComment)
            
            if needIndent:
                result += '\n'
            
            return result, needIndent
            
    
    def __init__(self, iterator = None, endComments = None):
        """Creates an tree from a key, value iterator if given, or an empty tree otherwise."""
        if iterator is None:
            self._data = []
        else:
            self._data = [Tree._Item(key, value) for (key, value) in iterator]
        
    # iterator methods
    def keys(self):
        """Iterator over the keys of this tree."""
        for item in self._data: yield item.key

    def values(self):
        """Iterator over the values of this tree."""
        for item in self._data: yield item.value

    def items(self, comments = False):
        """
        Iterator over (key, value) pairs of this tree.
        If comments = True, comments are emitted also.
        """
        if comments:
            for item in self._data: yield item.key, item.value, item.preComments, item.lineComment
        else:
            for item in self._data: yield item.key, item.value
        
    def comments(self):
        """Iterator over (key, value) pairs of this tree."""
        for item in self._data: yield item.preComments, item.lineComment

    def __contains__(self, key):
        """True iff key is in the top level of the tree."""
        return self.contains(key)
        
    def contains(self, key, *args, **kwargs):
        """True iff key is in the tree. recurse = True for recursive."""
        return self.find(key, *args, **kwargs) is not None

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

    def indexOf(self, key):
        for i, item in enumerate(self._data):
            if match(key, item.key): return i
        return None
        
    def count(self, key):
        """Count the number of items with matching key."""
        result = 0
        for i, item in enumerate(self._data):
            if match(key, item.key): result += 1
        return result
        
    def _find(self, key, *args, **kwargs):
        """Internal single find function. Returns a _Item."""
        it = self._findAll(key, *args, **kwargs)
        result = next(it, None)
        if result is None: raise KeyError('Key %s not found.' % key)
        return result 
        
    def _findAll(self, key, reverse = False, recurse = False):
        """Internal iterative find function. Iterates over _Items."""
        it = self._data
        if reverse: it = reversed(it)
        for item in it:
            if match(key, item.key): yield item
            if recurse and isinstance(item.value, Tree):
                for subitem in item.value._findAll(key, reverse = reverse, recurse = recurse): yield subitem
        
    def find(self, key, default = None, *args, **kwargs):
        """Return the first or last value corresponding to a key or None if not found"""
        it = self.findAll(key, *args, **kwargs)
        return next(it, default)

    def findAll(self, key, tupleLength = None, *args, **kwargs):
        """Return all values corresponding to a key. If set, tupleLength parameter causes this to yield tuples."""
        if tupleLength is None:
            for item in self._findAll(key, *args, **kwargs): 
                yield item.value
        else:
            partial = []
            for item in self._findAll(key, *args, **kwargs):
                partial.append(item.value)
                if len(partial) >= tupleLength:
                    yield tuple(x for x in partial)
                    partial = []

    def __getitem__(self, key):
        """Return the LAST value corresponding to a key or None if not found"""
        return self.find(key, reverse = True)

    # write methods
    def append(self, key, value, **kwargs):
        """Append a new key, value pair"""
        self._data.append(Tree._Item(key, value, **kwargs))

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
    
    def __iadd__(self, other):
        for item in other._data:
            self._data.append(copy.deepcopy(item))
        return self
            
    def __add__(self, other):
        result = copy.deepcopy(self)
        result += other
        return result

    # TODO: update
    
    def weakUpdate(self, other):
        # only updates if key isn't already in self
        for key, value in other.items():
            if key not in self:
                self.append(key, copy.deepcopy(value))
                
    def mergeItem(self, key, value, mergeLevels = 0):
        if key in self and isinstance(self[key], Tree):
            #print('Merge', value, 'into', self[key])
            self[key].merge(value, mergeLevels)
            #print('Result', self[key])
        else:
            self[key] = copy.deepcopy(value)
    
    # -1 for fully recursive merge
    def merge(self, other, mergeLevels = 0):
        if mergeLevels == 0:
            self += copy.deepcopy(other)
        else:
            for key, value in other.items():
                self.mergeItem(key, value, mergeLevels - 1)
    
    # comments
    
    def getPreComments(self, key):
        return self._find(key).preComments
    
    def getLineComment(self, key):
        return self._find(key).lineComment
        
    def getPostComments(self, key):
        return self._find(key).postComments
    
    def setPreComments(self, key, preComments):
        self._find(key).preComments = preComments
    
    def setLineComment(self, key, lineComment):
        self._find(key).lineComment = lineComment
        
    def setPostComments(self, key, postComments):
        self._find(key).postComments = postComments
        
    def getPreCommentsAt(self, i):
        return self._data[i].preComments
    
    def getLineCommentAt(self, i):
        return self._data[i].lineComment
        
    def getPostCommentsAt(self, i):
        return self._data[i].postComments
    
    def setPreCommentsAt(self, i, preComments):
        self._data[i].preComments = preComments
    
    def setLineCommentAt(self, i, lineComment):
        self._data[i].lineComment = lineComment
        
    def setPostCommentsAt(self, i, postComments):
        self._data[i].postComments = postComments
        
    # operator
    
    def getOperator(self, key):
        return self._find(key).operator
        
    def setOperator(self, key, operator):
        self._find(key).operator = operator
        
    def getOperatorAt(self, i):
        return self._data[i].operator
        
    def setOperatorAt(self, i, operator):
        self._data[i].operator = operator
    
    # string output methods
    def __str__(self):
        """Produces a string in the original .txt format."""
        return self.prettyprint(0)

    def rawData(self):
        raw = {}
        for item in self._data:
            if(item.key in raw):
                if type(raw[item.key]) is list :
                    raw[item.key].append(item.rawData())
                else :
                    raw[item.key] = [raw[item.key], item.rawData()]
            else :
                raw[item.key] = item.rawData()
        return raw

    def json(self):
        return json.dumps(self.rawData(),indent=2,sort_keys=True)

    def prettyprint(self, level = 0, indentString = '    ', includeComments = True):
        result = ''
        groupKey = None # The key corresponding to the current group. None if no group in progress.
        
        for item in self._data:
            if groupKey is not None: # Last item was in a group.
                if item.inGroup and match(item.key, groupKey) and not isinstance(item.value, Tree):
                    # Continue the previous group.
                    if needsIndent:
                        result += indentString * (level + 1)
                    groupString, needsIndent = item.prettyprintGroup(level = level + 1, indentString = indentString, includeComments = includeComments)
                    result += groupString
                    continue
                else:
                    # End the group.
                    groupKey = None
                    result += indentString * level + '}\n'
            if item.inGroup and not isinstance(item.value, Tree):
                # Start a group.
                groupKey = item.key
                result += '%s%s %s { ' % (indentString * level, item.key, item.operator)
                groupString, needsIndent = item.prettyprintGroup(level = level + 1, indentString = indentString, includeComments = includeComments)
                result += groupString
            else:
                result += item.prettyprint(level = level, indentString = indentString, includeComments = includeComments)
        
        # If last item was in a group, close it.
        if groupKey is not None:
            result += indentString * level + '}\n'

        return result

    # other methods
    def atDate(self, date = False, mergeLevels = -1):
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
                        result.mergeItem(item.key, item.value, mergeLevels)
        return result
            
def match(x, spec):
    if isinstance(spec, str) and isinstance(x, str): return x.lower() == spec.lower()
    else: return x == spec
