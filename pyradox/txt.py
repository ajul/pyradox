import pyradox.config
import pyradox.primitive
import pyradox.struct
import re
import os
import warnings

gameEncodings = {
    'EU4' : ['cp1252', 'utf_8_sig'],
    'HoI3' : ['cp1252', 'utf_8_sig'],
    'HoI3_vanilla' : ['cp1252', 'utf_8_sig'],
    'HoI4' : ['utf_8_sig', 'cp1252'],
    'HoI4_beta' : ['utf_8_sig', 'cp1252'],
}

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
        
def readlines(filename, encodings):
    for encoding in encodings:
        try:
            f = open(filename, encoding=encoding)
            lines = f.readlines()
            f.close()
            return lines
        except UnicodeDecodeError:
            warnings.warn(ParseWarning("Failed to decode input file %s using codec %s." % (filename, encoding)))
            f.close()
    raise ParseError("All codecs failed for input file %s." % filename)

def parse(s, filename=""):
    """Parse a string."""
    lines = s.splitlines()
    tokenData = lex(lines, filename)
    return parseTree(tokenData, filename)

def parseFile(filename, verbose=False, game=None):
    """Parse a single file and return a Tree."""
    if game is None: game = pyradox.config.getDefaultGame()
    encodings = gameEncodings[game]
    
    lines = readlines(filename, encodings)
    if verbose: print('Parsing file %s.' % filename)
    tokenData = lex(lines, filename)
    return parseTree(tokenData, filename)
    
def parseDir(dirname, verbose=False):
    """Given a directory, iterate over the content of the .txt files in that directory as Trees"""
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        if os.path.isfile(fullpath):
            _, ext = os.path.splitext(fullpath)
            if ext == ".txt":
                yield filename, parseFile(fullpath, verbose)

def parseMerge(dirname, verbose=False, mergeLevels = 0):
    """Given a directory, return a Tree as if all .txt files in the directory were a single file"""
    result = pyradox.struct.Tree()
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        if os.path.isfile(fullpath):
            _, ext = os.path.splitext(fullpath)
            if ext == ".txt":
                tree = parseFile(fullpath, verbose)
                result.merge(tree, mergeLevels)
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
    ('operator', r'[=><]'),
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

def parseTree(tokenData, filename, startPos = 0):
    """Given a list of (tokenType, tokenString, lineNumber) from the lexer, produces a Tree."""
    isTopLevel = (startPos == 0)
     # if starting position is 0, check for extra token at beginning
    if startPos == 0 and len(tokenData) >= 1 and tokenData[0][1] == 'EU4txt':
        tokenType, tokenString, lineNumber = tokenData[0]
        print('%s, line %d: Skipping header token "%s".' % (filename, lineNumber + 1, tokenString))
        startPos = 1 # skip first token
    
    result = pyradox.struct.Tree()
    pos = startPos
    prevLineNumber = -1
    preComments = []
    key = None
    keyString = None
    operator = None
    
    def stateKey(result, pos, prevLineNumber, preComments, key, keyString, operator, state):
        # expecting a key
        tokenType, tokenString, tokenLineNumber = tokenData[pos]
        pos += 1
        
        if pyradox.primitive.isPrimitiveKeyTokenType(tokenType):
            keyString = tokenString
            key = pyradox.primitive.makePrimitive(tokenString, tokenType)
            state = stateOperator
        elif tokenType == 'comment':
            if tokenLineNumber == prevLineNumber:
                result.setLineCommentAt(-1, tokenString[1:])
            else:
                preComments.append(tokenString[1:])
            state = stateKey
        elif tokenType == 'end':
            if isTopLevel:
                # top level cannot be ended, warn
                warnings.warn_explicit('Unmatched closing bracket. Skipping token.', ParseWarning, filename, tokenLineNumber + 1)
                state = stateKey
            else:
                state = None
        else:
            #invalid key
            warnings.warn_explicit('Token "%s" is not valid key. Skipping token.' % tokenString, ParseWarning, filename, tokenLineNumber + 1)
            state = stateKey
            
        prevLineNumber = tokenLineNumber

        return result, pos, prevLineNumber, preComments, key, keyString, operator, state
    
    def stateOperator(result, pos, prevLineNumber, preComments, key, keyString, operator, state):
        # expecting an operator
        tokenType, tokenString, tokenLineNumber = tokenData[pos]
        pos += 1
        
        if tokenType == 'operator':
            operator = tokenString
            state = stateValue
        elif tokenType == 'comment':
            preComments.append(tokenString[1:])
            state = stateOperator
        else:
            # missing operator; unconsume the token and move on
            warnings.warn_explicit('Expected operator after key "%s". Treating operator as "=" and token "%s" as value.' % (keyString, tokenString), ParseWarning, filename, tokenLineNumber + 1)
            pos -= 1
            operator = '='
            state = stateValue
            
        prevLineNumber = tokenLineNumber

        return result, pos, prevLineNumber, preComments, key, keyString, operator, state
    
    def stateValue(result, pos, prevLineNumber, preComments, key, keyString, operator, state):
        # expecting a value
        tokenType, tokenString, tokenLineNumber = tokenData[pos]
        pos += 1
        
        if pyradox.primitive.isPrimitiveValueTokenType(tokenType):
            if tokenString.lower() in ('hsv', 'rgb'):
                # Temporary hack.
                warnings.warn_explicit('Temporary hack to handle colors: Ignoring token "%s".' % tokenString, ParseWarning, filename, tokenLineNumber + 1)
                state = stateValue
            else:
                value = pyradox.primitive.makePrimitive(tokenString, tokenType)
                result.append(key, value, preComments = preComments, operator = operator)
                preComments = []
                state = stateKey
        elif tokenType == 'begin':
            # Value is a tree or group. First, determine whether this is a tree or group.
            lookaheadPos = pos
            level = 0
            # Empty brackets are trees.
            isTree = True
            while lookaheadPos < len(tokenData) and level >= 0:
                tokenType, tokenString, tokenLineNumber = tokenData[lookaheadPos]
                lookaheadPos += 1
                if tokenType == 'end':
                    level -= 1
                elif tokenType == 'comment':
                    continue
                else:
                    # Non-empty brackets are groups unless an operator is found.
                    isTree = False
                
                    if tokenType == 'begin':
                        # Assume any nesting indicates a tree.
                        isTree = True
                        break
                        # level += 1
                    elif tokenType == 'operator':
                        # Tree if operator detected at current level.
                        if level == 0: 
                            isTree = True
                            break
            
            if isTree:
                # Recurse.
                value, pos, tokenLineNumber = parseTree(tokenData, filename, pos)
                result.append(key, value, preComments = preComments, operator = operator)
                preComments = []
                state = stateKey
            else:
                # Go to group state.
                state = stateGroup
                
        elif tokenType == 'comment':
            preComments.append(tokenString[1:])
            state = stateValue
        else:
            raise ParseError('%s, line %d: Error: Invalid token type %s after key "%s", expected a value type.' % (filename, tokenLineNumber + 1, tokenType, keyString))
            
        prevLineNumber = tokenLineNumber

        return result, pos, prevLineNumber, preComments, key, keyString, operator, state
        
    def stateGroup(result, pos, prevLineNumber, preComments, key, keyString, operator, state):
        preComments = []
        tokenType, tokenString, tokenLineNumber = tokenData[pos]
        pos += 1
        
        if pyradox.primitive.isPrimitiveValueTokenType(tokenType):
            value = pyradox.primitive.makePrimitive(tokenString, tokenType)
            result.append(key, value, preComments = preComments, inGroup = True)
            preComments = []
        elif tokenType == "comment":
            if tokenLineNumber == prevLineNumber:
                result.setLineCommentAt(-1, tokenString[1:])
            else:
                preComments.append(tokenString[1:])
        elif tokenType == "end":
            result.endComments = preComments
            state = stateKey
        elif tokenType == "begin":
            raise ParseError('%s, line %d: Error: Cannot nest inside a group.' % (filename, tokenLineNumber + 1))
        else:
            raise ParseError('%s, line %d: Error: Invalid value type %s.' % (filename, tokenLineNumber + 1, tokenType))
        
        prevLineNumber = tokenLineNumber
        return result, pos, prevLineNumber, preComments, key, keyString, operator, state
        
    state = stateKey
    while pos < len(tokenData):
        result, pos, prevLineNumber, preComments, key, keyString, operator, state = state(result, pos, prevLineNumber, preComments, key, keyString, operator, state)
        if state is None: return result, pos, prevLineNumber
            
    # End of file reached.
    if isTopLevel:
        result.endComments = preComments
        return result
    else:
        raise ParseError('%s, line %d: Error: Cannot end inner level with end of file.' % (filename, prevLineNumber + 1))
