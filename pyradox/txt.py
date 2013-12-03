import pyradox.primitive
import pyradox.struct
import re
import os

def parseFile(filename, verbose=False):
    """Parse a single file and return a Tree."""
    f = open(filename)
    fileLines = f.readlines()
    f.close()
    if verbose: print('Parsing file %s.' % filename)
    tokenData = lex(fileLines, filename)
    return parse(tokenData, filename)
    
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
    ('comment', r'#'),
    ('whitespace', r'\s+'),
    ('equals', r'='),
    ('begin', r'\{'),
    ('end', r'\}'),
    # primitives
    ('date', r'\d{,4}\.\d{,2}\.\d{,2}\b'),
    ('float', r'-?(\d+\.\d*|\d*\.\d+)\b'),
    ('int', r'-?\d+\b'),
    ('bool', r'(yes|no)\b'),
    ('str', r'".*?"|[^#=\{\}\s]+\b'), # do escape characters exist?
    )

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
    """Lexer. Given the contents of a file, produces a list of (tokenType, tokenString, lineNumber)."""
    result = []
    for lineNumber, line in enumerate(fileLines):
        result += lexLine(line, filename, lineNumber)
    return result

def lexLine(line, filename, lineNumber):
    """Lex a single line."""
    result = []
    pos = 0
    while pos < len(line):
        # test vs keysymbols
        success = 0
        for tokenType, pattern in tokenTypes:
            m = re.match(pattern, line[pos:])
            if m is not None:
                tokenString = m.group(0)
                if tokenType == 'comment': return result
                if tokenType != 'whitespace':
                    result.append((tokenType, tokenString, lineNumber))
                    # print((tokenType, tokenString, lineNumber)) # debug
                pos += len(tokenString)
                break
        else:
            # default: show error and end line processing
            raise SyntaxError('%s, line %d: Error: Unrecognized token "%s".' % (filename, lineNumber + 1, line[pos:]))
    return result

def parse(tokenData, filename, startPos = 0):
    """Given a list of (tokenType, tokenString, lineNumber) from the lexer, produces a Tree or list as appropriate."""
    # determine whether is tree or list
    pos = startPos
    isEmpty = True
    while pos < len(tokenData):
        tokenType, tokenString, tokenLineNumber = tokenData[pos]
        pos += 1
        if tokenType == "equals":
            return parseAsTree(tokenData, filename, startPos)
        elif tokenType == "end":
            break
        elif tokenType in primitiveValues.keys():
            isEmpty = False
    
    if isEmpty: return parseAsTree(tokenData, filename, startPos) # empty defaults to tree
    else: return parseAsList(tokenData, filename, startPos)
    
def parseAsList(tokenData, filename, startPos = 0):
    """Parse a list from the tokenData."""
    result = pyradox.struct.List()
    pos = startPos
    while pos < len(tokenData):
        valueType, valueString, valueLineNumber = tokenData[pos]
        pos += 1
        if valueType == "end":
            if startPos == 0:
                # top level cannot be ended
                raise SyntaxError('%s, line %d: Error: Cannot end top level with closing bracket.' % (filename, keyLineNumber + 1))
            else:
                return result, pos
        elif valueType in primitiveValues.keys():
            value = primitiveValues[valueType](valueString)
            # nested lists possible?
        else:
            raise SyntaxError('%s, line %d: Error: Invalid value type %s. Only primitives are allowed in lists.' % (filename, keyLineNumber + 1, valueType))
        result.append(value)
    if startPos > 0:
        raise SyntaxError('%s, line %d: Error: Cannot end inner level with end of file.' % (filename, keyLineNumber + 1))
    else:
        return result
        
def parseAsTree(tokenData, filename, startPos = 0):
    """Parse a Tree from the tokenData."""
    result = pyradox.struct.Tree()
    pos = startPos
    while pos < len(tokenData):
        # read key
        keyType, keyString, keyLineNumber = tokenData[pos]
        pos += 1
        if keyType == "end":
            if startPos == 0:
                # top level cannot be ended
                raise SyntaxError('%s, line %d: Error: Cannot end top level with closing bracket.' % (filename, keyLineNumber + 1))
            else:
                return result, pos
        elif keyType in primitiveKeys.keys():
            key = primitiveKeys[keyType](keyString)
        else:
            #invalid key
            raise SyntaxError('%s, line %d: Error: Token type %s is not valid key.' % (filename, keyLineNumber + 1, keyType))

        if pos >= len(tokenData):
            raise SyntaxError('%s, line %d: Error: Reached end of file during key "%s".' % (filename, keyLineNumber + 1, keyString))

        # read equals sign
        equalsType, _, equalsLineNumber = tokenData[pos]
        if equalsType == "equals":
            pos += 1
        else:
            print('%s, line %d: Warning: Expected equals sign after key "%s".' % (filename, equalsLineNumber + 1, keyString))

        if pos >= len(tokenData):
            raise SyntaxError('%s, line %d: Error: Reached end of file during key "%s".' % (filename, keyLineNumber + 1, keyString))

        # read value
        valueType, valueString, valueLineNumber = tokenData[pos]
        pos += 1
        if valueType in primitiveValues.keys():
            value = primitiveValues[valueType](valueString)
        elif valueType == "begin":
            # value is a dict, recurse
            value, pos = parse(tokenData, filename, pos)
        else:
            raise SyntaxError('%s, line %d: Error: Invalid value type %s after key "%s".' % (filename, keyLineNumber + 1, valueType, keyString))
        result.append(key, value)
    if startPos > 0:
        raise SyntaxError('%s, line %d: Error: Cannot end inner level with end of file.' % (filename, keyLineNumber + 1))
    else:
        return result


