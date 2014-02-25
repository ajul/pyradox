import pyradox.primitive
import pyradox.struct
import re
import os
import warnings

class ParseError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class ParseWarning(Warning):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def parse(s, filename=""):
    """Parse a string."""
    lines = s.splitlines()
    tokenData = lex(lines, filename)
    return parseTokens(tokenData, filename)

def parseFile(filename, verbose=False):
    """Parse a single file and return a Tree."""
    f = open(filename)
    lines = f.readlines()
    f.close()
    if verbose: print('Parsing file %s.' % filename)
    tokenData = lex(lines, filename)
    return parseTokens(tokenData, filename)
    
def parseDir(dirname, verbose=False):
    """Given a directory, iterate over the content of the .txt files in that directory as Trees"""
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        if os.path.isfile(fullpath):
            root, ext = os.path.splitext(fullpath)
            if ext == ".txt":
                yield filename, parseFile(fullpath, verbose)

def parseMerge(dirname, verbose=False):
    """Given a directory, return a Tree as if all .txt files in the directory were a single file"""
    result = pyradox.struct.Tree()
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        if os.path.isfile(fullpath):
            root, ext = os.path.splitext(fullpath)
            if ext == ".txt":
                tree = parseFile(fullpath, verbose)
                result += tree
    return result

# open questions:
# what characters are allowed in key strings?
# in value strings?
# are there escape characters?

tokenTypes = (
    # keysymbols
    ('whitespace', r'\s+'),
    ('equals', r'='),
    ('begin', r'\{'),
    ('end', r'\}'),
    ('comment', r'#.*'),
    # primitives
    ('date', r'\d{,4}\.\d{,2}\.\d{,2}\b'),
    ('float', r'-?(\d+\.\d*|\d*\.\d+)\b'),
    ('int', r'-?\d+\b'),
    ('bool', r'(yes|no)\b'),
    ('str', r'".*?"|[^#=\{\}\s]+'), # do escape characters exist?
    )

omnibusPattern = ''
for tokenType, p in tokenTypes:
    omnibusPattern += '(?P<' + tokenType + '>' + p + ')'
    omnibusPattern += '|'
omnibusPattern += '(.+)'

omnibusPattern = re.compile(omnibusPattern)

primitiveKeys = {
    'date' : pyradox.primitive.Date,
    'int' : int,
    'str' : str,
    }

primitiveValues = {
    'date' : pyradox.primitive.Date,
    'float' : float,
    'int' : int,
    'bool' : pyradox.primitive.makeBool,
    'str' : pyradox.primitive.makeString,
    }

def lex(fileLines, filename):
    return list(lexIter(fileLines, filename))

def lexIter(fileLines, filename):
    """Lexer. Given the contents of a file, produces a list of (tokenType, tokenString, lineNumber)."""
    return (
        (m.lastgroup, m.group(0), lineNumber)
        for lineNumber, line in enumerate(fileLines)
        for m in omnibusPattern.finditer(line) if m.lastgroup not in ('whitespace', 'comment')
        )

def parseTokens(tokenData, filename, startPos = 0):
    """Given a list of (tokenType, tokenString, lineNumber) from the lexer, produces a Tree or list as appropriate."""
    isTopLevel = (startPos == 0)
    # if starting position is 0, check for extra token at beginning
    if startPos == 0 and len(tokenData) >= 3 and tokenData[2][0] == 'equals':
        tokenType, tokenString, lineNumber = tokenData[0]
        print('%s, line %d: Skipping header token "%s".' % (filename, lineNumber + 1, tokenString))
        startPos = 1 # skip first token
    # determine whether is tree or list
    pos = startPos
    isEmpty = True
    level = 0
    while pos < len(tokenData) and level >= 0:
        tokenType, tokenString, tokenLineNumber = tokenData[pos]
        pos += 1
        if tokenType == "end":
            level -= 1
        else:
            isEmpty = False
        
            if tokenType == "begin":
                level += 1
            elif tokenType == "equals":
                # parse as tree if equals sign detected at current level
                if level == 0: return parseAsTree(tokenData, filename, startPos, isTopLevel)
    
    if isEmpty: return parseAsTree(tokenData, filename, startPos, isTopLevel) # empty defaults to tree
    else: return parseAsList(tokenData, filename, startPos, isTopLevel)
    
def parseAsList(tokenData, filename, startPos = 0, isTopLevel = False):
    """Parse a list from the tokenData."""
    result = pyradox.struct.List()
    pos = startPos
    while pos < len(tokenData):
        valueType, valueString, valueLineNumber = tokenData[pos]
        pos += 1
        if valueType in primitiveValues.keys():
            value = primitiveValues[valueType](valueString)
        elif valueType == "end":
            if isTopLevel:
                # top level cannot be ended
                raise ParseError('%s, line %d: Error: Cannot end top level with closing bracket.' % (filename, keyLineNumber + 1))
            else:
                return result, pos
        elif valueType == "begin":
            value, pos = parseTokens(tokenData, filename, pos)
        else:
            raise ParseError('%s, line %d: Error: Invalid value type %s.' % (filename, keyLineNumber + 1, valueType))
        result.append(value)
    if isTopLevel:
        return result
    else:
        raise ParseError('%s, line %d: Error: Cannot end inner level with end of file.' % (filename, keyLineNumber + 1))
        
def parseAsTree(tokenData, filename, startPos = 0, isTopLevel = False):
    """Parse a Tree from the tokenData."""
    result = pyradox.struct.Tree()
    pos = startPos
    while pos < len(tokenData):
        # read key
        keyType, keyString, keyLineNumber = tokenData[pos]
        if keyType in primitiveKeys.keys():
            pos += 1
            key = primitiveKeys[keyType](keyString)
        elif keyType == "end":
            pos += 1
            if startPos == 0:
                # top level cannot be ended
                raise ParseError('%s, line %d: Error: Cannot end top level with closing bracket.' % (filename, keyLineNumber + 1))
            else:
                return result, pos
        else:
            #invalid key
            warnings.warn(ParseWarning('%s, line %d: Warning: Token "%s" is not valid key. Omitting corresponding value.' % (filename, keyLineNumber + 1, keyString)))
            key = None

        if pos >= len(tokenData):
            raise ParseError('%s, line %d: Error: Reached end of file during key "%s".' % (filename, keyLineNumber + 1, keyString))

        # read equals sign
        equalsType, _, equalsLineNumber = tokenData[pos]
        if equalsType == "equals":
            pos += 1
        else:
            if key is not None:
                warnings.warn(ParseWarning('%s, line %d: Warning: Expected equals sign after key "%s".' % (filename, equalsLineNumber + 1, keyString)))

        if pos >= len(tokenData):
            raise ParseError('%s, line %d: Error: Reached end of file during key "%s".' % (filename, keyLineNumber + 1, keyString))

        # read value
        valueType, valueString, valueLineNumber = tokenData[pos]
        pos += 1
        if valueType in primitiveValues.keys():
            value = primitiveValues[valueType](valueString)
        elif valueType == "begin":
            # value is a dict or list, recurse
            value, pos = parseTokens(tokenData, filename, pos)
        else:
            raise ParseError('%s, line %d: Error: Invalid value type %s after key "%s".' % (filename, keyLineNumber + 1, valueType, keyString))
        if key is not None:
            result.append(key, value)
    if isTopLevel:
        return result
    else:
        raise ParseError('%s, line %d: Error: Cannot end inner level with end of file.' % (filename, keyLineNumber + 1))
        


