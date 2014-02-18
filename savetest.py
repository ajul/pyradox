import os
import re
import collections
import pyradox.txt
import time
import warnings

def parseFile(filename):
    """Parse a single file and return a Tree."""
    f = open(filename)
    fileLines = f.readlines()
    f.close()
    startTime = time.clock()
    print('Lexing file %s.' % filename)
    tokenData = list(pyradox.txt.lex(fileLines, filename))
    lexTime = time.clock()
    print('Lexed in %ss.' % (lexTime - startTime))
    print('Parsing file %s.' % filename)
    result = pyradox.txt.parse(tokenData, filename)
    parseTime = time.clock()
    print('Parsed in %ss.' % (parseTime - lexTime))
    return result

warnings.simplefilter("ignore", pyradox.txt.ParseWarning)
savetree = parseFile('in/thebloke.eu4')
print(savetree["checksum"])

