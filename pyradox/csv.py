import csv
import os
import warnings
import pyradox.primitive
import pyradox.struct
import pyradox.table

encoding = 'cp1252'

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

class ParadoxDialect(csv.Dialect):
    delimiter = ';'
    lineterminator = '\n'
    quoting = csv.QUOTE_NONE # no quotes AFAICT
    strict = True

def parseFile(filename, verbose=False):
    f = open(filename, encoding=encoding)
    lines = f.readlines()
    f.close()
    if verbose: print('Parsing file %s.' % filename)
    return parse(lines, filename)
    
def parseDir(dirname, verbose=False):
    """Given a directory, iterate over the content of the .csv files in that directory"""
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        if os.path.isfile(fullpath):
            _, ext = os.path.splitext(fullpath)
            if ext == ".csv":
                yield filename, parseFile(fullpath, verbose)

def parse(lines, filename):
    reader = csv.reader(lines, dialect = ParadoxDialect)
    headingTokens = next(reader, None)
    if headingTokens is None:
        raise ParseError('%s, row 1 (headings): csv file must have at least one row' % filename)
    headings = [x.lower() for x in headingTokens[:-1]]
    result = pyradox.table.Table(headings)
    for i, rowTokens in enumerate(reader):
        rowTokens = rowTokens[:-1]
        if len(rowTokens) == 0: continue
        if len(rowTokens) != len(headings):
            warnings.warn(ParseWarning('%s, row %d: row length (%d) should be same as headings length (%d)' % (filename, i + 2, len(rowTokens), len(headings))))
            for i in range(len(rowTokens), len(headings)):
                rowTokens.append('')
            rowTokens = rowTokens[:len(headings)]
        result.addRow([pyradox.primitive.makePrimitive(token, defaultTokenType = 'str') for token in rowTokens])
    return result 
    
