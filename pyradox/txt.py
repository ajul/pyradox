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
            _, ext = os.path.splitext(fullpath)
            if ext == ".txt":
                yield filename, parseFile(fullpath, verbose)

def parseMerge(dirname, verbose=False):
    """Given a directory, return a Tree as if all .txt files in the directory were a single file"""
    result = pyradox.struct.Tree()
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        if os.path.isfile(fullpath):
            _, ext = os.path.splitext(fullpath)
            if ext == ".txt":
                tree = parseFile(fullpath, verbose)
                result += tree
    return result

def parseWalk(dirname, verbose=False):
    """Given a directory, recursively iterate over the content of the .txt files in that directory as Trees"""
    for root, dirs, files in os.walk(dirname):
        for filename in files:
            fullpath = os.path.join(root, filename)
            _, ext = os.path.splitext(fullpath)
            if ext == ".txt":
                yield filename, parseFile(fullpath, verbose)

# open questions:
# what characters are allowed in key strings?
# in value strings?
# are there escape characters?

tokenTypes = [
    # keysymbols
    ('whitespace', r'\s+'),
    ('equals', r'='),
    ('begin', r'\{'),
    ('end', r'\}'),
    ('comment', r'#.*'),
    ] + pyradox.primitive.tokenPatterns

omnibusPattern = ''
for tokenType, p in tokenTypes:
    omnibusPattern += '(?P<' + tokenType + '>' + p + ')'
    omnibusPattern += '|'
omnibusPattern += '(.+)'

omnibusPattern = re.compile(omnibusPattern)

def lex(fileLines, filename):
    return list(lexIter(fileLines, filename))

def lexIter(fileLines, filename):
    """Lexer. Given the contents of a file, produces a list of (tokenType, tokenString, lineNumber)."""
    return (
        (m.lastgroup, m.group(0), lineNumber)
        for lineNumber, line in enumerate(fileLines)
        for m in omnibusPattern.finditer(line) if m.lastgroup not in ('whitespace',)
        )

def parseTokens(tokenData, filename, startPos = 0):
    """Given a list of (tokenType, tokenString, lineNumber) from the lexer, produces a Tree or list as appropriate."""
    isTopLevel = (startPos == 0)
    # if starting position is 0, check for extra token at beginning
    if startPos == 0 and len(tokenData) >= 1 and tokenData[0][1] == 'EU4txt':
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
        if tokenType == 'end':
            level -= 1
        elif tokenType == 'comment':
            continue
        else:
            isEmpty = False
        
            if tokenType == 'begin':
                level += 1
            elif tokenType == 'equals':
                # parse as tree if equals sign detected at current level
                if level == 0: return parseAsTree(tokenData, filename, startPos, isTopLevel)
    
    if isEmpty: return parseAsTree(tokenData, filename, startPos, isTopLevel) # empty defaults to tree
    else: return parseAsList(tokenData, filename, startPos, isTopLevel)
    
def parseAsList(tokenData, filename, startPos = 0, isTopLevel = False):
    """Parse a list from the tokenData. Returns the list, end position, and end line number."""
    result = pyradox.struct.List()
    pos = startPos
    prevLineNumber = -1
    preComments = []
    while pos < len(tokenData):
        tokenType, tokenString, tokenLineNumber = tokenData[pos]
        pos += 1
        
        if pyradox.primitive.isPrimitiveValueTokenType(tokenType):
            value = pyradox.primitive.makePrimitive(tokenString, tokenType)
            result.append(value, preComments = preComments)
            preComments = []
        elif tokenType == "comment":
            if tokenLineNumber == prevLineNumber:
                result.setLineComment(-1, tokenString[1:])
            else:
                preComments.append(tokenString[1:])
        elif tokenType == "end":
            if isTopLevel:
                # top level cannot be ended, warn
                warnings.warn(ParseWarning('%s, line %d: Warning: Unmatched closing bracket.' % (filename, tokenLineNumber + 1)))
            else:
                result.endComments = preComments
                return result, pos, tokenLineNumber
        elif tokenType == "begin":
            value, pos, tokenLineNumber = parseTokens(tokenData, filename, pos)
            result.append(value, preComments = preComments)
            preComments = []
        else:
            raise ParseError('%s, line %d: Error: Invalid value type %s.' % (filename, tokenLineNumber + 1, tokenType))
        
        prevLineNumber = tokenLineNumber
    
    # End of file reached.
    if isTopLevel:
        result.endComments = preComments
        return result
    else:
        raise ParseError('%s, line %d: Error: Cannot end inner level with end of file.' % (filename, prevLineNumber + 1))
        
def parseAsTree(tokenData, filename, startPos = 0, isTopLevel = False):
    """Parse a Tree from the tokenData."""
    
    result = pyradox.struct.Tree()
    pos = startPos
    prevLineNumber = -1
    preComments = []
    key = None
    keyString = None
    
    def stateKey():
        # expecting a key
        nonlocal result, pos, prevLineNumber, preComments, key, keyString, state
        tokenType, tokenString, tokenLineNumber = tokenData[pos]
        pos += 1
        
        if pyradox.primitive.isPrimitiveKeyTokenType(tokenType):
            keyString = tokenString
            key = pyradox.primitive.makePrimitive(tokenString, tokenType)
            state = stateEquals
        elif tokenType == 'comment':
            if tokenLineNumber == prevLineNumber:
                result.setLineCommentAt(-1, tokenString[1:])
            else:
                preComments.append(tokenString[1:])
            state = stateKey
        elif tokenType == 'end':
            if isTopLevel:
                # top level cannot be ended, warn
                warnings.warn(ParseWarning('%s, line %d: Warning: Unmatched closing bracket. Skipping token.' % (filename, tokenLineNumber + 1)))
            state = None
        else:
            #invalid key
            warnings.warn(ParseWarning('%s, line %d: Warning: Token "%s" is not valid key. Skipping token.' % (filename, tokenLineNumber + 1, tokenString)))
            state = stateKey
            
        prevLineNumber = tokenLineNumber
    
    def stateEquals():
        # expecting an equals sign
        nonlocal result, pos, prevLineNumber, preComments, key, keyString, state
        tokenType, tokenString, tokenLineNumber = tokenData[pos]
        pos += 1
        
        if tokenType == 'equals':
            state = stateValue
        elif tokenType == 'comment':
            preComments.append(tokenString[1:])
            state = stateEquals
        else:
            # missing equals sign; unconsume the token and move on
            warnings.warn(ParseWarning('%s, line %d: Warning: Expected equals sign after key "%s". Treating token "%s" as value.' % (filename, tokenLineNumber + 1, keyString, tokenString)))
            pos -= 1
            state = stateValue
            
        prevLineNumber = tokenLineNumber
    
    def stateValue():
        # expecting a value
        nonlocal result, pos, prevLineNumber, preComments, key, keyString, state
        tokenType, tokenString, tokenLineNumber = tokenData[pos]
        pos += 1
        
        if pyradox.primitive.isPrimitiveValueTokenType(tokenType):
            value = pyradox.primitive.makePrimitive(tokenString, tokenType)
            result.append(key, value, preComments = preComments)
            preComments = []
            state = stateKey
        elif tokenType == 'begin':
            # value is a dict or list, recurse
            value, pos, tokenLineNumber = parseTokens(tokenData, filename, pos)
            result.append(key, value, preComments = preComments)
            preComments = []
            state = stateKey
        elif tokenType == 'comment':
            preComments.append(tokenString[1:])
            state = stateValue
        else:
            raise ParseError('%s, line %d: Error: Invalid token type %s after key "%s", expected a value type.' % (filename, tokenLineNumber + 1, tokenType, keyString))
            
        prevLineNumber = tokenLineNumber
        
    state = stateKey
    while pos < len(tokenData):
        state()
        if state is None: return result, pos, prevLineNumber
            
    # End of file reached.
    if isTopLevel:
        result.endComments = preComments
        return result
    else:
        raise ParseError('%s, line %d: Error: Cannot end inner level with end of file.' % (filename, prevLineNumber + 1))
        


